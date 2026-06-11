"""Build semantic SVG/P&ID models for the ABACUS P&ID viewer.

The parser treats the SVG XML as the engineering source. It extracts colour-line
bins, coarse semantic layers, subsystem hints, text/tag evidence, and directional
arrows only when SVG geometry or marker evidence exists. Uncertain arrow or line
associations are recorded as unresolved rather than silently inferred.
"""

from __future__ import annotations

import argparse
import html
import json
import math
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.inkscape_input_bridge import build_bridge_manifest, write_bridge_manifest  # noqa: E402

EXPECTED_SVG_INPUTS = [
    Path("data/svg/PFD-PID MINERVA QCELL-LB.svg"),
    Path("data/svg/PFD-PID MINERVA RFCELL seen by ACR.svg"),
]
EXPECTED_PPT_INPUTS = [
    Path("data/ppt/PFD-PID of RFCELL - MASTER.pptx"),
    Path("data/ppt/PID MINERVA CryoCell (QCELL-LB).pptx"),
    Path("data/ppt/QSYS (and RFCELL) instrumentation location for LB and LBI.pptx"),
]

MODEL_DIR = Path("data/model")
LINES_DIR = MODEL_DIR / "lines"
REPORTS_DIR = Path("reports")
PUBLISH_DIR = Path("publish")
VIEWER_DIR = Path("viewer")

LINE_OUTPUTS = {
    "blue_A": LINES_DIR / "blue_A.json",
    "cyan_B_2K": LINES_DIR / "cyan_B_2K.json",
    "green_W_coupler": LINES_DIR / "green_W_coupler.json",
    "grey_V_vent": LINES_DIR / "grey_V_vent.json",
    "olive_S_line": LINES_DIR / "olive_S_line.json",
    "red_orange_D_E": LINES_DIR / "red_orange_D_E.json",
    "unknown_black_or_other": LINES_DIR / "unknown_black_or_other.json",
}

LINE_BINS = {
    "blue_A": {
        "label": "A / A′ 4.5 K line",
        "toggle": "A / A′ 4.5 K line",
        "style": "stroke-dasharray:none;",
        "palette": [(0, 70, 170), (30, 110, 230), (60, 130, 255)],
    },
    "cyan_B_2K": {
        "label": "B / B′ 2 K line",
        "toggle": "B / B′ 2 K line",
        "style": "stroke-dasharray:8 4;",
        "palette": [(0, 170, 210), (0, 200, 255), (80, 220, 255)],
    },
    "green_W_coupler": {
        "label": "W coupler line",
        "toggle": "W coupler line",
        "style": "stroke-dasharray:2 4;",
        "palette": [(0, 120, 40), (0, 150, 70), (60, 180, 90)],
    },
    "grey_V_vent": {
        "label": "V vent line",
        "toggle": "V vent line",
        "style": "stroke-dasharray:10 4 2 4;",
        "palette": [(90, 90, 90), (130, 130, 130), (170, 170, 170)],
    },
    "olive_S_line": {
        "label": "S line",
        "toggle": "S line",
        "style": "stroke-dasharray:12 3;",
        "palette": [(90, 110, 20), (120, 140, 35), (150, 160, 60)],
    },
    "red_orange_D_E": {
        "label": "D/E manifold lines",
        "toggle": "D/E manifold lines",
        "style": "stroke-dasharray:4 3;",
        "palette": [(180, 30, 20), (220, 80, 20), (240, 130, 20)],
    },
    "unknown_black_or_other": {
        "label": "unknown/black/structure",
        "toggle": "unknown/black/structure",
        "style": "stroke-dasharray:1 3;",
        "palette": [(0, 0, 0), (40, 40, 40), (80, 80, 80)],
    },
}

SEMANTIC_TOGGLES = [
    "full drawing",
    "colour/process lines",
    "A / A′ 4.5 K line",
    "B / B′ 2 K line",
    "W coupler line",
    "S line",
    "V vent line",
    "D/E manifold lines",
    "unknown/black/structure",
    "instruments only",
    "valves only",
    "equipment only",
    "boundaries only",
    "vacuum barrier",
    "QM section",
    "Jumper section",
    "QVB section",
    "QINFRA/interface section",
    "arrows / flow direction only",
    "unresolved items",
]

TAG_RE = re.compile(
    r"\b(?:[A-Z]{1,5}[.-]?\d{1,4}[A-Z]?|[A-Z]{1,5}[.-][A-Z0-9]{1,8}|Q(?:M|VB|INFRA|CELL|SYS|RB|DIST)\b)"
)
SUBSYSTEM_RE = re.compile(
    r"\b(QM|QVB|QINFRA|JUMPER|VACUUM|BARRIER|INTERFACE|QCELL|RFCELL)\b", re.I
)
COLOUR_RE = re.compile(
    r"#[0-9a-fA-F]{3,8}|rgba?\([^)]*\)|\b(?:black|blue|cyan|green|grey|gray|olive|red|orange)\b"
)
NUM_RE = re.compile(r"-?\d+(?:\.\d+)?")
SVG_NS = "http://www.w3.org/2000/svg"


@dataclass
class LineRecord:
    line_id: str
    source_file: str
    source_svg_element_id: str
    element_tag: str
    colour_bin: str
    source_colour: str
    semantic_label: str
    subsystem: str | None
    coordinates: dict[str, Any]
    confidence: float
    evidence: list[str] = field(default_factory=list)
    unresolved_reason: str | None = None


@dataclass
class ArrowRecord:
    arrow_id: str
    source_file: str
    source_svg_element_id: str
    source_colour: str | None
    start_body_coordinate: list[float] | None
    arrow_tip_coordinate: list[float] | None
    inferred_direction: str | None
    line_id: str | None
    subsystem: str | None
    confidence: float
    evidence: list[str] = field(default_factory=list)
    unresolved_reason: str | None = None


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1] if "}" in tag else tag


def parse_style(style: str | None) -> dict[str, str]:
    out: dict[str, str] = {}
    if not style:
        return out
    for chunk in style.split(";"):
        if not chunk.strip():
            continue
        sep = ":" if ":" in chunk else "=" if "=" in chunk else None
        if sep:
            key, value = chunk.split(sep, 1)
            out[key.strip()] = value.strip()
        else:
            out[chunk.strip()] = "true"
    return out


def colour_from_element(element: ET.Element) -> str | None:
    style = parse_style(element.attrib.get("style"))
    for key in ("stroke", "fill", "color", "strokeColor", "fillColor"):
        value = element.attrib.get(key) or style.get(key)
        if value and value.lower() not in {"none", "transparent"}:
            match = COLOUR_RE.search(value)
            return match.group(0) if match else value
    return None


def rgb_from_colour(colour: str | None) -> tuple[int, int, int] | None:
    if not colour:
        return None
    value = colour.strip().lower()
    names = {
        "black": (0, 0, 0),
        "blue": (0, 90, 220),
        "cyan": (0, 200, 255),
        "green": (0, 150, 70),
        "grey": (130, 130, 130),
        "gray": (130, 130, 130),
        "olive": (120, 140, 35),
        "red": (220, 30, 20),
        "orange": (240, 130, 20),
    }
    if value in names:
        return names[value]
    if value.startswith("#"):
        hex_value = value[1:]
        if len(hex_value) == 3:
            hex_value = "".join(ch * 2 for ch in hex_value)
        if len(hex_value) >= 6:
            return tuple(int(hex_value[i : i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]
    if value.startswith("rgb"):
        nums = [int(float(num)) for num in NUM_RE.findall(value)[:3]]
        if len(nums) == 3:
            return tuple(nums)  # type: ignore[return-value]
    return None


def colour_distance(a: tuple[int, int, int], b: tuple[int, int, int]) -> float:
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def classify_colour(colour: str | None) -> tuple[str, float, list[str]]:
    rgb = rgb_from_colour(colour)
    if rgb is None:
        return (
            "unknown_black_or_other",
            0.2,
            ["no supported stroke/fill colour evidence"],
        )
    best_bin = "unknown_black_or_other"
    best_distance = float("inf")
    for bin_name, info in LINE_BINS.items():
        for palette_rgb in info["palette"]:
            dist = colour_distance(rgb, palette_rgb)
            if dist < best_distance:
                best_distance = dist
                best_bin = bin_name
    confidence = max(0.3, min(0.98, 1.0 - best_distance / 260.0))
    evidence = [
        f"colour {colour!r} mapped to {best_bin} by RGB nearest-palette distance {best_distance:.1f}"
    ]
    if best_distance > 95:
        return (
            "unknown_black_or_other",
            min(confidence, 0.45),
            evidence + ["colour distance exceeded semantic threshold"],
        )
    return best_bin, confidence, evidence


def element_id(element: ET.Element, fallback: str) -> str:
    return element.attrib.get("id") or fallback


def is_line_like(tag: str) -> bool:
    return tag in {"path", "line", "polyline", "polygon"}


def is_boundary_like(tag: str, element: ET.Element) -> bool:
    style = parse_style(element.attrib.get("style"))
    stroke_width = element.attrib.get("stroke-width") or style.get("stroke-width") or ""
    klass = (element.attrib.get("class") or "").lower()
    text = " ".join(element.itertext()).lower()
    return tag in {"rect", "g"} and (
        "boundary" in klass
        or "barrier" in klass
        or "vacuum" in text
        or any(num and float(num) >= 2.5 for num in NUM_RE.findall(stroke_width)[:1])
    )


def coords_for_element(element: ET.Element) -> dict[str, Any]:
    tag = local_name(element.tag)
    if tag == "line":
        return {
            "start": [
                float(element.attrib.get("x1", 0)),
                float(element.attrib.get("y1", 0)),
            ],
            "end": [
                float(element.attrib.get("x2", 0)),
                float(element.attrib.get("y2", 0)),
            ],
        }
    if tag in {"polyline", "polygon"}:
        nums = [float(num) for num in NUM_RE.findall(element.attrib.get("points", ""))]
        points = [[nums[i], nums[i + 1]] for i in range(0, len(nums) - 1, 2)]
        return {
            "points": points,
            "start": points[0] if points else None,
            "end": points[-1] if points else None,
        }
    if tag == "path":
        nums = [float(num) for num in NUM_RE.findall(element.attrib.get("d", ""))]
        points = [[nums[i], nums[i + 1]] for i in range(0, len(nums) - 1, 2)]
        return {
            "points": points,
            "start": points[0] if points else None,
            "end": points[-1] if points else None,
        }
    return {}


def infer_subsystem(
    text_context: str, element_id_value: str
) -> tuple[str | None, list[str]]:
    haystack = f"{text_context} {element_id_value}"
    match = SUBSYSTEM_RE.search(haystack)
    if not match:
        return None, []
    raw = match.group(1).upper()
    mapping = {
        "BARRIER": "vacuum_barrier",
        "VACUUM": "vacuum_barrier",
        "INTERFACE": "QINFRA/interface",
        "JUMPER": "Jumper",
    }
    subsystem = mapping.get(raw, raw)
    return subsystem, [f"subsystem text/id evidence: {match.group(0)!r}"]


def classify_layer(
    tag: str, element: ET.Element, text: str, colour_bin: str | None
) -> tuple[str, list[str]]:
    element_id_value = element.attrib.get("id", "")
    klass = (element.attrib.get("class") or "").lower()
    combined = f"{text} {element_id_value} {klass}".lower()
    if tag == "text" or TAG_RE.search(text):
        return "tags", ["text/tag regex evidence"]
    if "valve" in combined or re.search(r"\b(?:v|cv|pv|sv|xv)[.-]?\d+", combined, re.I):
        return "valves", ["valve text/id evidence"]
    if "instrument" in combined or re.search(
        r"\b(?:pt|tt|ft|lt|pi|ti|fi|li)[.-]?\d+", combined, re.I
    ):
        return "instruments", ["instrument tag evidence"]
    if "equipment" in combined or re.search(
        r"\b(?:hx|vessel|pump|compressor|cryocell|qcell|rfcell)\b", combined, re.I
    ):
        return "equipment", ["equipment text/id evidence"]
    if is_boundary_like(tag, element):
        return "boundaries", ["boundary/vacuum visual or text evidence"]
    if colour_bin:
        return "colour/process lines", [f"line colour bin evidence: {colour_bin}"]
    return "unknown/black/structure", ["no stronger semantic layer evidence"]


def find_text_nodes(root: ET.Element) -> list[dict[str, Any]]:
    tags: list[dict[str, Any]] = []
    for idx, element in enumerate(root.iter()):
        if local_name(element.tag) not in {"text", "tspan"}:
            continue
        text = " ".join(" ".join(element.itertext()).split())
        if not text:
            continue
        matches = TAG_RE.findall(text)
        tags.append(
            {
                "tag_id": element_id(element, f"text_{idx}"),
                "text": text,
                "matches": matches,
                "layer": "tags" if matches else "text",
                "confidence": 0.9 if matches else 0.55,
                "evidence": ["SVG text node evidence"],
                "unresolved_reason": (
                    None if matches else "text node did not match known tag regex"
                ),
            }
        )
    return tags


def marker_evidence(element: ET.Element) -> tuple[str | None, list[str]]:
    style = parse_style(element.attrib.get("style"))
    for attr in ("marker-end", "marker-start", "marker-mid"):
        value = element.attrib.get(attr) or style.get(attr)
        if value and value.lower() != "none":
            return attr, [f"{attr}={value!r}"]
    return None, []


def infer_arrow(
    element: ET.Element, line: LineRecord, arrow_index: int
) -> ArrowRecord | None:
    marker_attr, evidence = marker_evidence(element)
    coords = line.coordinates
    start = coords.get("start")
    end = coords.get("end")
    points = coords.get("points") or []
    if not marker_attr and local_name(element.tag) not in {"polygon", "polyline"}:
        return None

    inferred = None
    tip = None
    body = None
    confidence = 0.0
    unresolved = None
    if marker_attr == "marker-end" and start and end:
        inferred = "start-to-end"
        body = start
        tip = end
        confidence = 0.86
    elif marker_attr == "marker-start" and start and end:
        inferred = "end-to-start"
        body = end
        tip = start
        confidence = 0.86
    elif marker_attr == "marker-mid" and len(points) >= 3:
        inferred = "polyline-mid-marker"
        body = points[0]
        tip = points[-1]
        confidence = 0.62
        unresolved = "mid-marker direction is approximate and not fully associated with a unique tip"
    elif local_name(element.tag) == "polygon" and len(points) >= 3:
        tip = max(points, key=lambda point: point[0])
        body = min(points, key=lambda point: point[0])
        inferred = "polygon-arrowhead-tip-estimate"
        confidence = 0.48
        unresolved = "polygon arrowhead has geometry but no marker-start/end evidence"
        evidence.append(
            "polygon geometry suggests arrowhead but direction is not definitive"
        )
    else:
        unresolved = (
            "arrow marker present but start/tip coordinates could not be extracted"
        )
        confidence = 0.25

    return ArrowRecord(
        arrow_id=f"arrow_{arrow_index:04d}",
        source_file=line.source_file,
        source_svg_element_id=line.source_svg_element_id,
        source_colour=line.source_colour,
        start_body_coordinate=body,
        arrow_tip_coordinate=tip,
        inferred_direction=inferred if confidence >= 0.6 and not unresolved else None,
        line_id=line.line_id if confidence >= 0.6 else None,
        subsystem=line.subsystem if confidence >= 0.6 else None,
        confidence=confidence,
        evidence=evidence,
        unresolved_reason=unresolved,
    )


def parse_svg(svg_path: Path) -> dict[str, Any]:
    root = ET.parse(svg_path).getroot()
    all_text = " ".join(" ".join(root.itertext()).split())
    lines: list[LineRecord] = []
    arrows: list[ArrowRecord] = []
    layer_items: dict[str, list[str]] = defaultdict(list)
    subsystem_items: dict[str, list[str]] = defaultdict(list)
    boundaries: list[str] = []
    tags = find_text_nodes(root)
    unresolved_items: list[dict[str, Any]] = []

    for idx, element in enumerate(root.iter()):
        tag = local_name(element.tag)
        elem_id = element_id(element, f"svg_{idx:05d}")
        text = " ".join(" ".join(element.itertext()).split())
        colour = colour_from_element(element)
        colour_bin = None
        if is_line_like(tag):
            colour_bin, colour_confidence, colour_evidence = classify_colour(colour)
            subsystem, subsystem_evidence = infer_subsystem(
                f"{all_text} {text}", elem_id
            )
            coords = coords_for_element(element)
            unresolved_reason = None
            if colour_bin == "unknown_black_or_other" and colour_confidence < 0.5:
                unresolved_reason = (
                    "colour could not be confidently mapped to a process-line bin"
                )
                unresolved_items.append(
                    {"id": elem_id, "type": "colour", "reason": unresolved_reason}
                )
            line = LineRecord(
                line_id=f"line_{len(lines) + 1:04d}",
                source_file=str(svg_path),
                source_svg_element_id=elem_id,
                element_tag=tag,
                colour_bin=colour_bin,
                source_colour=colour or "unresolved",
                semantic_label=LINE_BINS[colour_bin]["label"],
                subsystem=subsystem,
                coordinates=coords,
                confidence=colour_confidence,
                evidence=colour_evidence + subsystem_evidence,
                unresolved_reason=unresolved_reason,
            )
            lines.append(line)
            layer_items["colour/process lines"].append(elem_id)
            layer_items[LINE_BINS[colour_bin]["toggle"]].append(elem_id)
            if subsystem:
                subsystem_items[subsystem].append(elem_id)
            arrow = infer_arrow(element, line, len(arrows) + 1)
            if arrow:
                arrows.append(arrow)
                layer_items["arrows / flow direction only"].append(arrow.arrow_id)
                if arrow.unresolved_reason:
                    unresolved_items.append(
                        {
                            "id": arrow.arrow_id,
                            "type": "arrow",
                            "reason": arrow.unresolved_reason,
                        }
                    )
            continue

        layer, layer_evidence = classify_layer(tag, element, text, None)
        if layer in {"instruments", "valves", "equipment", "boundaries", "tags"}:
            layer_items[layer].append(elem_id)
        if layer == "boundaries":
            boundaries.append(elem_id)
        subsystem, subsystem_evidence = infer_subsystem(text, elem_id)
        if subsystem:
            subsystem_items[subsystem].append(elem_id)
            if subsystem == "vacuum_barrier":
                layer_items["vacuum barrier"].append(elem_id)
            if subsystem in {"QM", "QVB", "Jumper", "QINFRA/interface"}:
                layer_items[f"{subsystem} section"].append(elem_id)
        if layer == "unknown/black/structure" and (
            layer_evidence or subsystem_evidence
        ):
            pass

    for tag in tags:
        if tag["unresolved_reason"]:
            unresolved_items.append(
                {"id": tag["tag_id"], "type": "tag", "reason": tag["unresolved_reason"]}
            )

    return {
        "source_file": str(svg_path),
        "svg_load_status": "loaded",
        "file_size_bytes": svg_path.stat().st_size,
        "lines": [asdict(line) for line in lines],
        "arrows": [asdict(arrow) for arrow in arrows],
        "tags": tags,
        "layer_items": {name: items for name, items in layer_items.items()},
        "subsystem_items": {name: items for name, items in subsystem_items.items()},
        "boundaries": boundaries,
        "unresolved_items": unresolved_items,
    }


def input_inventory(paths: Iterable[Path]) -> list[dict[str, Any]]:
    inventory = []
    for path in paths:
        exists = path.exists()
        inventory.append(
            {
                "path": str(path),
                "found": exists,
                "size_bytes": path.stat().st_size if exists else None,
            }
        )
    return inventory


def build_models(svg_paths: list[Path] | None = None) -> dict[str, Any]:
    expected_svg = svg_paths or EXPECTED_SVG_INPUTS
    found_svg = [path for path in expected_svg if path.exists()]
    parsed = []
    load_errors = []
    for path in found_svg:
        try:
            parsed.append(parse_svg(path))
        except (
            Exception
        ) as exc:  # noqa: BLE001 - reports must preserve load failure evidence.
            load_errors.append(
                {"path": str(path), "svg_load_status": "failed", "error": str(exc)}
            )

    lines = [line for item in parsed for line in item["lines"]]
    arrows = [arrow for item in parsed for arrow in item["arrows"]]
    tags = [tag for item in parsed for tag in item["tags"]]
    unresolved_items = [
        unresolved for item in parsed for unresolved in item["unresolved_items"]
    ]
    unresolved_items.extend(
        {"id": err["path"], "type": "svg_load", "reason": err["error"]}
        for err in load_errors
    )
    if not found_svg:
        unresolved_items.append(
            {
                "id": "expected_svg_inputs",
                "type": "input",
                "reason": "No expected SVG inputs were found under data/svg/",
            }
        )

    line_counter = Counter(line["colour_bin"] for line in lines)
    arrow_counter = Counter(arrow["source_colour"] or "unresolved" for arrow in arrows)
    layer_items: dict[str, set[str]] = {toggle: set() for toggle in SEMANTIC_TOGGLES}
    subsystem_items: dict[str, set[str]] = {
        "vacuum barrier": set(),
        "QM": set(),
        "Jumper": set(),
        "QVB": set(),
        "QINFRA/interface": set(),
    }
    for item in parsed:
        for layer, ids in item["layer_items"].items():
            layer_items.setdefault(layer, set()).update(ids)
        for subsystem, ids in item["subsystem_items"].items():
            subsystem_items.setdefault(subsystem, set()).update(ids)
    layer_items["full drawing"].update(line["line_id"] for line in lines)
    layer_items["unresolved items"].update(item["id"] for item in unresolved_items)

    line_model = {
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "input_files": input_inventory(EXPECTED_SVG_INPUTS + EXPECTED_PPT_INPUTS),
        "svg_load_status": [
            {"path": item["source_file"], "status": item["svg_load_status"]}
            for item in parsed
        ]
        + load_errors,
        "lines": lines,
        "colour_bins": {
            name: {"count": line_counter.get(name, 0), **info}
            for name, info in LINE_BINS.items()
        },
        "unresolved_colours": [line for line in lines if line.get("unresolved_reason")],
    }
    semantic_layer_model = {
        "toggles": [
            {
                "toggle": toggle,
                "item_count": len(layer_items.get(toggle, set())),
                "item_ids": sorted(layer_items.get(toggle, set())),
            }
            for toggle in SEMANTIC_TOGGLES
        ],
        "layers": {toggle: sorted(ids) for toggle, ids in layer_items.items()},
        "confidence_notes": [
            "Semantic correctness is claimed only where colour, geometry, tag, or boundary evidence is recorded.",
            "Unmapped items remain visible in unresolved/unknown bins rather than being silently inferred.",
        ],
    }
    subsystem_model = {
        "subsystems": [
            {"subsystem": name, "item_count": len(ids), "item_ids": sorted(ids)}
            for name, ids in sorted(subsystem_items.items())
        ],
        "subsystem_count": sum(1 for ids in subsystem_items.values() if ids),
    }
    arrow_direction_model = {
        "arrows": arrows,
        "counts": {
            "total": len(arrows),
            "resolved": sum(
                1
                for arrow in arrows
                if not arrow.get("unresolved_reason")
                and arrow.get("inferred_direction")
            ),
            "unresolved": sum(
                1
                for arrow in arrows
                if arrow.get("unresolved_reason") or not arrow.get("inferred_direction")
            ),
        },
        "counts_by_source_colour": dict(arrow_counter),
    }
    tag_layer_register = {
        "tags": tags,
        "tag_count": len(tags),
        "resolved_tag_count": sum(
            1 for tag in tags if not tag.get("unresolved_reason")
        ),
        "unresolved_tag_count": sum(1 for tag in tags if tag.get("unresolved_reason")),
    }

    return {
        "parsed": parsed,
        "line_model": line_model,
        "semantic_layer_model": semantic_layer_model,
        "subsystem_model": subsystem_model,
        "arrow_direction_model": arrow_direction_model,
        "tag_layer_register": tag_layer_register,
        "unresolved_items": unresolved_items,
    }


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_models(models: dict[str, Any]) -> list[Path]:
    outputs = [
        (MODEL_DIR / "line_model.json", models["line_model"]),
        (MODEL_DIR / "semantic_layer_model.json", models["semantic_layer_model"]),
        (MODEL_DIR / "subsystem_model.json", models["subsystem_model"]),
        (MODEL_DIR / "arrow_direction_model.json", models["arrow_direction_model"]),
        (MODEL_DIR / "tag_layer_register.json", models["tag_layer_register"]),
    ]
    lines_by_bin: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for line in models["line_model"]["lines"]:
        lines_by_bin[line["colour_bin"]].append(line)
    for bin_name, path in LINE_OUTPUTS.items():
        outputs.append(
            (
                path,
                {
                    "colour_bin": bin_name,
                    "line_count": len(lines_by_bin[bin_name]),
                    "lines": lines_by_bin[bin_name],
                },
            )
        )
    written = []
    for path, data in outputs:
        write_json(path, data)
        written.append(path)
    return written


def report_common(models: dict[str, Any], title: str) -> list[str]:
    line_model = models["line_model"]
    arrow_model = models["arrow_direction_model"]
    tag_model = models["tag_layer_register"]
    subsystem_model = models["subsystem_model"]
    lines = [f"# {title}", ""]
    lines.append("## Actual input files found")
    lines.append("")
    for item in line_model["input_files"]:
        status = "found" if item["found"] else "missing"
        lines.append(f"- `{item['path']}` — {status}; size={item['size_bytes']}")
    lines.append("")
    bridge_manifest = line_model.get("inkscape_bridge_manifest")
    if bridge_manifest:
        lines.append("## Inkscape bridge")
        lines.append("")
        lines.append(f"- Bridge manifest: `{bridge_manifest}`")
        lines.append(
            "- Inkscape defaults/fabric are inventoried from an operator-supplied source tree or zip when provided; parser execution keeps SVG XML as source."
        )
        lines.append("")

    lines.append("## SVG load status")
    lines.append("")
    if line_model["svg_load_status"]:
        for item in line_model["svg_load_status"]:
            lines.append(
                f"- `{item['path']}` — {item.get('status') or item.get('svg_load_status')}"
            )
    else:
        lines.append("- No SVG inputs loaded.")
    lines.extend(
        [
            "",
            "## Counts",
            "",
            f"- Colour bins detected: {sum(1 for info in line_model['colour_bins'].values() if info['count'])}",
            f"- Path/line counts per colour: {json.dumps({name: info['count'] for name, info in line_model['colour_bins'].items()}, sort_keys=True)}",
            f"- Arrow counts per colour: {json.dumps(arrow_model['counts_by_source_colour'], sort_keys=True)}",
            f"- Tag counts: {tag_model['tag_count']} total; {tag_model['unresolved_tag_count']} unresolved",
            f"- Subsystem counts: {subsystem_model['subsystem_count']} populated subsystem bin(s)",
            f"- Boundary counts: {len([item for toggle in models['semantic_layer_model']['toggles'] if toggle['toggle'] == 'boundaries only' for item in toggle['item_ids']])}",
            f"- Unresolved arrows: {arrow_model['counts']['unresolved']}",
            f"- Unresolved colours: {len(line_model['unresolved_colours'])}",
            f"- Unresolved tags: {tag_model['unresolved_tag_count']}",
            "",
            "## Confidence notes",
            "",
            "- Semantic correctness is not claimed without colour/process, arrow geometry, tag text, or boundary/scope evidence.",
            "- Uncertain arrow association is marked unresolved rather than inferred.",
            "",
            "## Known gaps",
            "",
        ]
    )
    if not any(
        item["found"] for item in line_model["input_files"][: len(EXPECTED_SVG_INPUTS)]
    ):
        lines.append(
            "- Expected SVG source files are not present in `data/svg/`; generated models are empty preparation artifacts."
        )
    else:
        lines.append(
            "- PPTX inputs are inventoried but not parsed in W002/W003 viewer preparation."
        )
        lines.append(
            "- Geometry association remains conservative; ambiguous arrows stay unresolved."
        )
    return lines


def write_reports(models: dict[str, Any]) -> list[Path]:
    reports = {
        REPORTS_DIR / "W002_colour_line_validation.md": "W002 Colour Line Validation",
        REPORTS_DIR
        / "W003_semantic_layer_validation.md": "W003 Semantic Layer Validation",
        REPORTS_DIR
        / "W003_arrow_direction_validation.md": "W003 Arrow Direction Validation",
    }
    written = []
    for path, title in reports.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            "\n".join(report_common(models, title)) + "\n", encoding="utf-8"
        )
        written.append(path)
    return written


def first_svg_markup() -> str:
    for path in EXPECTED_SVG_INPUTS:
        if path.exists():
            return path.read_text(encoding="utf-8", errors="replace")
    return "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1200 800'><rect width='1200' height='800' fill='#fff'/><text x='60' y='90' font-size='28'>No expected P&amp;ID SVG input found in data/svg/</text></svg>"


def viewer_html(models: dict[str, Any]) -> str:
    svg = first_svg_markup()
    model_json = json.dumps(
        {
            "line_model": models["line_model"],
            "semantic_layer_model": models["semantic_layer_model"],
            "subsystem_model": models["subsystem_model"],
            "arrow_direction_model": models["arrow_direction_model"],
            "tag_layer_register": models["tag_layer_register"],
        },
        sort_keys=True,
    )
    controls = "\n".join(
        f"<label><input type='checkbox' data-toggle='{html.escape(toggle)}' checked> {html.escape(toggle)}</label>"
        for toggle in SEMANTIC_TOGGLES
    )
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>ABACUS P&amp;ID Semantic Viewer</title>
<style>
  :root {{ color-scheme: light; --panel:#f8fafc; --line:#0f172a; }}
  body {{ margin:0; font-family: Arial, sans-serif; color:#111827; background:#e5e7eb; }}
  header {{ padding:12px 16px; background:#111827; color:white; }}
  main {{ display:grid; grid-template-columns:320px 1fr 320px; gap:10px; padding:10px; }}
  aside, section {{ background:white; border:1px solid #cbd5e1; border-radius:8px; padding:10px; }}
  label {{ display:block; margin:6px 0; font-size:13px; }}
  #canvas {{ overflow:auto; max-height:calc(100vh - 96px); }}
  #svg-host svg {{ max-width:none; background:white; }}
  .meta {{ font-family: ui-monospace, SFMono-Regular, Menlo, monospace; white-space:pre-wrap; font-size:12px; }}
  .mono-safe {{ stroke-dasharray: var(--semantic-dash, none); }}
  @page {{ size: A3 landscape; margin: 10mm; }}
  @media print {{ main {{ display:block; }} aside {{ display:none; }} #canvas {{ max-height:none; overflow:visible; }} }}
</style>
</head>
<body>
<header><strong>ABACUS P&amp;ID Semantic Viewer</strong> — original SVG preserved; semantic toggles hide/show extracted bins.</header>
<main>
<aside>
  <h2>Toggles</h2>
  {controls}
  <h2>Search by tag</h2>
  <input id="tag-search" placeholder="PT, TT, QVB..." style="width:100%;box-sizing:border-box">
  <div id="search-results"></div>
</aside>
<section id="canvas"><div id="svg-host">{svg}</div></section>
<aside>
  <h2>Metadata</h2>
  <pre id="metadata" class="meta">Click an SVG item or search result.</pre>
  <h2>Unresolved items</h2>
  <div id="unresolved" class="meta"></div>
</aside>
</main>
<script id="semantic-model" type="application/json">{html.escape(model_json)}</script>
<script>
const model = JSON.parse(document.getElementById('semantic-model').textContent);
const allLines = new Map(model.line_model.lines.map(item => [item.source_svg_element_id, item]));
const tags = model.tag_layer_register.tags || [];
const unresolved = [
  ...(model.line_model.unresolved_colours || []),
  ...(model.arrow_direction_model.arrows || []).filter(a => a.unresolved_reason),
  ...tags.filter(t => t.unresolved_reason)
];
const toggleMap = Object.fromEntries(model.semantic_layer_model.toggles.map(t => [t.toggle, new Set(t.item_ids)]));
function findBySvgId(id) {{ return model.line_model.lines.find(x => x.source_svg_element_id === id) || tags.find(x => x.tag_id === id) || model.arrow_direction_model.arrows.find(x => x.source_svg_element_id === id); }}
function setVisibleByIds(ids, visible) {{ ids.forEach(id => {{ const el = document.getElementById(id); if (el) el.style.display = visible ? '' : 'none'; }}); }}
function applyToggles() {{
  document.querySelectorAll('input[data-toggle]').forEach(input => {{
    const ids = toggleMap[input.dataset.toggle] || new Set();
    setVisibleByIds(ids, input.checked);
  }});
}}
document.querySelectorAll('input[data-toggle]').forEach(input => input.addEventListener('change', applyToggles));
document.getElementById('svg-host').addEventListener('click', event => {{
  const target = event.target.closest('[id]');
  const meta = target ? findBySvgId(target.id) || {{ source_svg_element_id: target.id, note: 'No extracted metadata for clicked element.' }} : {{ note:'No SVG element id.' }};
  document.getElementById('metadata').textContent = JSON.stringify(meta, null, 2);
}});
document.getElementById('tag-search').addEventListener('input', event => {{
  const q = event.target.value.toLowerCase();
  const matches = q ? tags.filter(t => (t.text || '').toLowerCase().includes(q) || (t.matches || []).join(' ').toLowerCase().includes(q)).slice(0, 30) : [];
  document.getElementById('search-results').innerHTML = matches.map(t => `<button data-id="${{t.tag_id}}">${{t.text}}</button>`).join('<br>');
}});
document.getElementById('search-results').addEventListener('click', event => {{
  if (!event.target.dataset.id) return;
  const meta = tags.find(t => t.tag_id === event.target.dataset.id);
  document.getElementById('metadata').textContent = JSON.stringify(meta, null, 2);
}});
document.getElementById('unresolved').textContent = JSON.stringify(unresolved, null, 2);
</script>
</body>
</html>
"""


def write_html(models: dict[str, Any]) -> list[Path]:
    html_text = viewer_html(models)
    VIEWER_DIR.mkdir(parents=True, exist_ok=True)
    PUBLISH_DIR.mkdir(parents=True, exist_ok=True)
    viewer_path = VIEWER_DIR / "index.html"
    collage_path = PUBLISH_DIR / "colour_line_collage.html"
    viewer_path.write_text(html_text, encoding="utf-8")
    collage_path.write_text(
        html_text.replace("Semantic Viewer", "Colour Line Collage"), encoding="utf-8"
    )
    return [collage_path, viewer_path]


def run(
    *,
    input_zip: Path | None = None,
    inkscape_source: Path | None = None,
    repo_url: str | None = None,
) -> dict[str, Any]:
    bridge_manifest = None
    if input_zip is not None or inkscape_source is not None or repo_url is not None:
        bridge_manifest = build_bridge_manifest(
            input_zip=input_zip,
            inkscape_source=inkscape_source,
            repo_url=repo_url or DEFAULT_INKSCAPE_REPO_URL,
        )
        write_bridge_manifest(bridge_manifest)
    models = build_models()
    if bridge_manifest is not None:
        models["line_model"][
            "inkscape_bridge_manifest"
        ] = "data/model/inkscape_bridge_manifest.json"
        write_json(MODEL_DIR / "line_model.json", models["line_model"])
    model_paths = write_models(models)
    report_paths = write_reports(models)
    html_paths = write_html(models)
    return {
        "models": models,
        "model_paths": model_paths,
        "report_paths": report_paths,
        "html_paths": html_paths,
    }


DEFAULT_INKSCAPE_REPO_URL = "https://gitlab.com/inkscape/inkscape/-/tree/master"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build ABACUS P&ID semantic layer models and viewer prep artifacts"
    )
    parser.add_argument(
        "--input-zip",
        type=Path,
        help="Zip containing expected SVG/PPT source inputs to extract before parsing",
    )
    parser.add_argument(
        "--inkscape-source",
        type=Path,
        help="Local Inkscape source tree or source zip to inventory for defaults/fabric",
    )
    parser.add_argument(
        "--repo-url",
        default=None,
        help="GBOGEB fork or upstream Inkscape repository URL reference",
    )
    args = parser.parse_args(argv)
    result = run(
        input_zip=args.input_zip,
        inkscape_source=args.inkscape_source,
        repo_url=args.repo_url,
    )
    print("Generated model files:")
    for path in result["model_paths"]:
        print(f"- {path}")
    print("Generated reports:")
    for path in result["report_paths"]:
        print(f"- {path}")
    print("Generated HTML files:")
    for path in result["html_paths"]:
        print(f"- {path}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
