#!/usr/bin/env python3
"""Extract conservative semantic layers from ABACUS P&ID SVG inputs.

The extractor is intentionally evidence-first: colours, tags, boundaries, and
arrow directions are recorded only from observable SVG geometry/text. Anything
that cannot be associated is carried as unresolved metadata for viewer review.
"""
from __future__ import annotations

import json
import math
import re
import statistics
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SVG_INPUTS = [
    ROOT / "data/svg/PFD-PID MINERVA QCELL-LB.svg",
    ROOT / "data/svg/PFD-PID MINERVA RFCELL seen by ACR.svg",
]
PPT_INPUTS = [
    ROOT / "data/ppt/PFD-PID of RFCELL - MASTER.pptx",
    ROOT / "data/ppt/PID MINERVA CryoCell (QCELL-LB).pptx",
    ROOT / "data/ppt/QSYS (and RFCELL) instrumentation location for LB and LBI.pptx",
]
MODEL_DIR = ROOT / "data/model"
LINES_DIR = MODEL_DIR / "lines"
REPORTS_DIR = ROOT / "reports"
PUBLISH_DIR = ROOT / "publish"
VIEWER_DIR = ROOT / "viewer"

LINE_BIN_FILES = {
    "blue_A": "blue_A.json",
    "cyan_B_2K": "cyan_B_2K.json",
    "green_W_coupler": "green_W_coupler.json",
    "grey_V_vent": "grey_V_vent.json",
    "olive_S_line": "olive_S_line.json",
    "red_orange_D_E": "red_orange_D_E.json",
    "unknown_black_or_other": "unknown_black_or_other.json",
}

NS_RE = re.compile(r"^\{.*\}")
COORD_RE = re.compile(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?")
TRANS_RE = re.compile(r"translate\(([-+]?\d*\.?\d+)(?:[,\s]+([-+]?\d*\.?\d+))?")
TAG_RE = re.compile(r"\b(?:[A-Z]{1,5}[-_ ]?)?\d{2,}[A-Z0-9_.-]*\b|\b(?:QM|QVB|QINFRA|JUMPER|RFCELL|QCELL|ACR)\b", re.I)
STYLE_SPLIT_RE = re.compile(r"\s*;\s*")


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def strip(tag: str) -> str:
    return NS_RE.sub("", tag)


def parse_style(style: str | None) -> dict[str, str]:
    out: dict[str, str] = {}
    if not style:
        return out
    for part in STYLE_SPLIT_RE.split(style.strip()):
        if ":" in part:
            key, value = part.split(":", 1)
            out[key.strip().lower()] = value.strip()
    return out


def attr(el: ET.Element, name: str) -> str | None:
    return el.attrib.get(name) or parse_style(el.attrib.get("style")).get(name)


def norm_colour(value: str | None) -> str:
    if not value:
        return "none"
    value = value.strip().lower()
    named = {
        "black": "#000000", "white": "#ffffff", "blue": "#0000ff", "cyan": "#00ffff",
        "aqua": "#00ffff", "green": "#008000", "grey": "#808080", "gray": "#808080",
        "olive": "#808000", "red": "#ff0000", "orange": "#ffa500", "none": "none",
    }
    if value in named:
        return named[value]
    if value.startswith("#"):
        if len(value) == 4:
            return "#" + "".join(ch * 2 for ch in value[1:])
        if len(value) >= 7:
            return value[:7]
    m = re.match(r"rgba?\(([^)]+)\)", value)
    if m:
        nums = [float(x.strip().rstrip("%")) for x in m.group(1).split(",")[:3]]
        if "%" in m.group(1):
            nums = [n * 2.55 for n in nums]
        return "#" + "".join(f"{max(0,min(255,int(round(n)))):02x}" for n in nums)
    return value


def rgb(hex_colour: str) -> tuple[int, int, int] | None:
    if re.match(r"^#[0-9a-f]{6}$", hex_colour):
        return int(hex_colour[1:3], 16), int(hex_colour[3:5], 16), int(hex_colour[5:7], 16)
    return None


def colour_bin(colour: str) -> tuple[str, str, float]:
    c = norm_colour(colour)
    r = rgb(c)
    if not r:
        return "unknown_black_or_other", "unknown/black/structure", 0.2
    red, green, blue = r
    if blue > 120 and red < 120 and green < 170:
        return "blue_A", "A / A′ 4.5 K line", 0.75
    if blue > 130 and green > 130 and red < 120:
        return "cyan_B_2K", "B / B′ 2 K line", 0.75
    if green > 100 and red < 120 and blue < 130:
        return "green_W_coupler", "W coupler line", 0.7
    if abs(red - green) < 25 and abs(green - blue) < 25 and 70 <= red <= 210:
        return "grey_V_vent", "V vent line", 0.65
    if red > 80 and green > 80 and blue < 100 and abs(red - green) < 80:
        return "olive_S_line", "S line", 0.65
    if red > 150 and green < 170 and blue < 120:
        return "red_orange_D_E", "D/E manifold lines", 0.7
    return "unknown_black_or_other", "unknown/black/structure", 0.35


def numbers(value: str | None) -> list[float]:
    if not value:
        return []
    return [float(x) for x in COORD_RE.findall(value)]


def points_for(el: ET.Element) -> list[tuple[float, float]]:
    tag = strip(el.tag)
    if tag == "line":
        vals = [el.attrib.get(k) for k in ("x1", "y1", "x2", "y2")]
        if all(v is not None for v in vals):
            return [(float(vals[0]), float(vals[1])), (float(vals[2]), float(vals[3]))]  # type: ignore[arg-type]
    if tag in {"polyline", "polygon"}:
        vals = numbers(el.attrib.get("points"))
        return list(zip(vals[0::2], vals[1::2]))
    if tag == "path":
        vals = numbers(el.attrib.get("d"))
        return list(zip(vals[0::2], vals[1::2]))
    if tag == "rect":
        x, y = float(el.attrib.get("x", 0)), float(el.attrib.get("y", 0))
        w, h = float(el.attrib.get("width", 0)), float(el.attrib.get("height", 0))
        return [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
    return []


def bbox(points: list[tuple[float, float]]) -> dict[str, float] | None:
    if not points:
        return None
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return {"x_min": min(xs), "y_min": min(ys), "x_max": max(xs), "y_max": max(ys)}


def midpoint(points: list[tuple[float, float]]) -> tuple[float, float] | None:
    if not points:
        return None
    return (statistics.mean([p[0] for p in points]), statistics.mean([p[1] for p in points]))


def dist(a: tuple[float, float], b: tuple[float, float]) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def infer_subsystem(text: str, box: dict[str, float] | None = None) -> str:
    t = text.upper()
    if "QINFRA" in t or "INTERFACE" in t:
        return "QINFRA/interface section"
    if "JUMPER" in t:
        return "Jumper section"
    if "QVB" in t or "VACUUM" in t:
        return "QVB section"
    if "QM" in t:
        return "QM section"
    return "unresolved subsystem"


def element_id(el: ET.Element, fallback: str) -> str:
    return el.attrib.get("id") or fallback


def extract_svg(svg_path: Path, input_index: int) -> dict[str, Any]:
    try:
        tree = ET.parse(svg_path)
    except Exception as exc:  # noqa: BLE001
        return {"path": rel(svg_path), "status": "load_error", "error": str(exc), "lines": [], "arrows": [], "tags": [], "boundaries": []}
    root = tree.getroot()
    lines: list[dict[str, Any]] = []
    arrows: list[dict[str, Any]] = []
    tags: list[dict[str, Any]] = []
    boundaries: list[dict[str, Any]] = []
    all_text: list[str] = []

    for idx, el in enumerate(root.iter()):
        tag = strip(el.tag)
        eid = element_id(el, f"svg{input_index}_{tag}_{idx}")
        stroke = norm_colour(attr(el, "stroke"))
        fill = norm_colour(attr(el, "fill"))
        pts = points_for(el)
        box = bbox(pts)
        style = parse_style(el.attrib.get("style"))
        dash = el.attrib.get("stroke-dasharray") or style.get("stroke-dasharray")

        if tag in {"path", "line", "polyline"} and stroke not in {"none", "#ffffff"} and pts:
            bin_id, layer, conf = colour_bin(stroke)
            line_id = f"line_{len(lines)+1:05d}"
            lines.append({
                "line_id": line_id,
                "source_file": rel(svg_path),
                "source_svg_element_id": eid,
                "element_type": tag,
                "source_colour": stroke,
                "colour_bin": bin_id,
                "semantic_layer": layer,
                "points_sample": pts[:12],
                "bbox": box,
                "subsystem": "unresolved subsystem",
                "confidence": conf,
                "evidence": [f"stroke={stroke}", f"element={tag}"],
                "unresolved_reason": None if bin_id != "unknown_black_or_other" else "Colour is black/other or not mapped to a named process line.",
            })
            marker = el.attrib.get("marker-end") or el.attrib.get("marker-start") or style.get("marker-end") or style.get("marker-start")
            if marker:
                start, end = pts[0], pts[-1]
                tip = end if "marker-end" in el.attrib or "marker-end" in style else start
                body = start if tip == end else end
                arrows.append({
                    "arrow_id": f"arrow_{len(arrows)+1:05d}",
                    "source_file": rel(svg_path),
                    "source_svg_element_id": eid,
                    "source_colour": stroke,
                    "start_body_coordinate": body,
                    "arrow_tip_coordinate": tip,
                    "inferred_direction": "body_to_tip",
                    "line_id": line_id,
                    "subsystem": "unresolved subsystem",
                    "confidence": 0.82,
                    "evidence": [f"SVG marker attribute on {tag}", f"marker={marker}", "line endpoints available"],
                    "unresolved_reason": None,
                })

        if tag == "path" and pts and fill not in {"none", "#ffffff"} and len(pts) >= 3:
            xs = [p[0] for p in pts[:3]]
            ys = [p[1] for p in pts[:3]]
            area_box = bbox(pts[:4])
            if area_box and (area_box["x_max"] - area_box["x_min"] <= 40) and (area_box["y_max"] - area_box["y_min"] <= 40):
                arrows.append({
                    "arrow_id": f"arrow_{len(arrows)+1:05d}",
                    "source_file": rel(svg_path),
                    "source_svg_element_id": eid,
                    "source_colour": fill if fill != "none" else stroke,
                    "start_body_coordinate": midpoint(pts),
                    "arrow_tip_coordinate": pts[0] if len(set(xs)) > 1 and len(set(ys)) > 1 else None,
                    "inferred_direction": None,
                    "line_id": None,
                    "subsystem": "unresolved subsystem",
                    "confidence": 0.38,
                    "evidence": ["Small filled path resembles possible arrow head", "No connected body line proven"],
                    "unresolved_reason": "Possible arrow head is not confidently associated with a process line.",
                })

        if tag == "text":
            text = "".join(el.itertext()).strip()
            if text:
                all_text.append(text)
                m = TRANS_RE.search(el.attrib.get("transform", ""))
                tx = float(el.attrib.get("x", m.group(1) if m else 0) or 0)
                ty = float(el.attrib.get("y", m.group(2) if m and m.group(2) else 0) or 0)
                tag_matches = TAG_RE.findall(text)
                tag_id = f"tag_{len(tags)+1:05d}"
                subsystem = infer_subsystem(text)
                tags.append({
                    "tag_id": tag_id,
                    "source_file": rel(svg_path),
                    "source_svg_element_id": eid,
                    "text": text,
                    "detected_tokens": tag_matches,
                    "coordinate": [tx, ty],
                    "semantic_class": "tag" if tag_matches else "annotation_or_label",
                    "subsystem": subsystem,
                    "confidence": 0.8 if tag_matches else 0.45,
                    "evidence": ["SVG text element", "tag regex match" if tag_matches else "no tag regex match"],
                    "unresolved_reason": None if tag_matches else "Text could not be classified as a tag by conservative regex.",
                })

        if tag in {"rect", "polygon", "polyline", "path"} and box and (dash or tag == "rect"):
            width = box["x_max"] - box["x_min"]
            height = box["y_max"] - box["y_min"]
            if width > 100 and height > 80:
                boundaries.append({
                    "boundary_id": f"boundary_{len(boundaries)+1:05d}",
                    "source_file": rel(svg_path),
                    "source_svg_element_id": eid,
                    "element_type": tag,
                    "bbox": box,
                    "stroke": stroke,
                    "subsystem": "unresolved subsystem",
                    "semantic_layer": "boundaries only",
                    "confidence": 0.55 if dash else 0.35,
                    "evidence": ["large enclosing geometry", "dashed stroke" if dash else "rectangle geometry"],
                    "unresolved_reason": "Boundary/scope label not directly associated." if not dash else None,
                })

    # Assign nearest explicit subsystem labels to line/arrow/boundary when text evidence is close.
    subsystem_tags = [t for t in tags if t["subsystem"] != "unresolved subsystem"]
    for collection in (lines, boundaries):
        for item in collection:
            center = midpoint([(item["bbox"]["x_min"], item["bbox"]["y_min"]), (item["bbox"]["x_max"], item["bbox"]["y_max"])]) if item.get("bbox") else None
            if center and subsystem_tags:
                nearest = min(subsystem_tags, key=lambda t: dist(center, tuple(t["coordinate"])))
                if dist(center, tuple(nearest["coordinate"])) < 450:
                    item["subsystem"] = nearest["subsystem"]
                    item["evidence"].append(f"nearest subsystem text: {nearest['text']}")
    line_by_id = {l["line_id"]: l for l in lines}
    for arrow in arrows:
        if arrow.get("line_id") and arrow["line_id"] in line_by_id:
            arrow["subsystem"] = line_by_id[arrow["line_id"]]["subsystem"]
        elif arrow.get("arrow_tip_coordinate"):
            tip = tuple(arrow["arrow_tip_coordinate"])
            candidates = [(dist(tip, p), l) for l in lines for p in (l.get("points_sample") or [])]
            if candidates:
                d, line = min(candidates, key=lambda x: x[0])
                if d < 15:
                    arrow["line_id"] = line["line_id"]
                    arrow["subsystem"] = line["subsystem"]
                    arrow["confidence"] = min(arrow["confidence"], 0.6)
                    arrow["evidence"].append(f"nearest sampled line point within {d:.1f}px")
                    arrow["unresolved_reason"] = "Arrow head proximity association only; direction body not proven."
    return {"path": rel(svg_path), "status": "loaded", "lines": lines, "arrows": arrows, "tags": tags, "boundaries": boundaries, "text": all_text[:500]}


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def markdown_table(rows: list[list[Any]], headers: list[str]) -> str:
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    out += ["| " + " | ".join(str(c) for c in row) + " |" for row in rows]
    return "\n".join(out)


def build_models() -> dict[str, Any]:
    found_inputs = [{"path": rel(p), "size_bytes": p.stat().st_size, "kind": "svg"} for p in SVG_INPUTS if p.exists()]
    found_inputs += [{"path": rel(p), "size_bytes": p.stat().st_size, "kind": "ppt"} for p in PPT_INPUTS if p.exists()]
    missing_inputs = [rel(p) for p in [*SVG_INPUTS, *PPT_INPUTS] if not p.exists()]

    svg_results = [extract_svg(p, i) for i, p in enumerate(SVG_INPUTS, start=1) if p.exists()]
    lines = [l for r in svg_results for l in r["lines"]]
    arrows = [a for r in svg_results for a in r["arrows"]]
    tags = [t for r in svg_results for t in r["tags"]]
    boundaries = [b for r in svg_results for b in r["boundaries"]]

    for item in lines:
        item["viewer_layer_ids"] = ["full_drawing", "colour_process_lines", item["colour_bin"], item["subsystem"].lower().replace(" ", "_").replace("/", "_")]
    for item in arrows:
        bin_id, layer, _ = colour_bin(item.get("source_colour"))
        item["colour_bin"] = bin_id
        item["semantic_layer"] = "arrows / flow direction only"
        item["viewer_layer_ids"] = ["arrows_flow_direction", bin_id]

    colour_counts = Counter(l["colour_bin"] for l in lines)
    arrow_colour_counts = Counter(a.get("colour_bin", "unknown_black_or_other") for a in arrows)
    subsystem_counts = Counter([x["subsystem"] for x in [*lines, *tags, *boundaries] if x.get("subsystem")])
    tag_counts = Counter(t["semantic_class"] for t in tags)
    unresolved_arrows = [a for a in arrows if a.get("unresolved_reason") or not a.get("line_id") or not a.get("inferred_direction")]
    unresolved_colours = [l for l in lines if l["colour_bin"] == "unknown_black_or_other"]
    unresolved_tags = [t for t in tags if t.get("unresolved_reason")]

    run = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "inputs_found": found_inputs,
        "inputs_missing": missing_inputs,
        "svg_load_status": [{"path": r["path"], "status": r["status"], "error": r.get("error")} for r in svg_results] or [{"path": rel(p), "status": "missing"} for p in SVG_INPUTS],
    }

    line_model = {"schema_version": "0.1", **run, "summary": {"line_count": len(lines), "colour_counts": dict(colour_counts)}, "lines": lines}
    arrow_model = {"schema_version": "0.1", **run, "summary": {"arrow_count": len(arrows), "arrow_colour_counts": dict(arrow_colour_counts), "unresolved_arrow_count": len(unresolved_arrows)}, "arrows": arrows}
    layers = [
        {"layer_id": "full_drawing", "label": "full drawing", "item_count": len(lines)+len(tags)+len(boundaries)+len(arrows)},
        {"layer_id": "colour_process_lines", "label": "colour/process lines", "item_count": len(lines)},
        {"layer_id": "blue_A", "label": "A / A′ 4.5 K line", "item_count": colour_counts.get("blue_A", 0)},
        {"layer_id": "cyan_B_2K", "label": "B / B′ 2 K line", "item_count": colour_counts.get("cyan_B_2K", 0)},
        {"layer_id": "green_W_coupler", "label": "W coupler line", "item_count": colour_counts.get("green_W_coupler", 0)},
        {"layer_id": "olive_S_line", "label": "S line", "item_count": colour_counts.get("olive_S_line", 0)},
        {"layer_id": "grey_V_vent", "label": "V vent line", "item_count": colour_counts.get("grey_V_vent", 0)},
        {"layer_id": "red_orange_D_E", "label": "D/E manifold lines", "item_count": colour_counts.get("red_orange_D_E", 0)},
        {"layer_id": "unknown_black_or_other", "label": "unknown/black/structure", "item_count": colour_counts.get("unknown_black_or_other", 0)},
        {"layer_id": "instruments_only", "label": "instruments only", "item_count": tag_counts.get("tag", 0)},
        {"layer_id": "valves_only", "label": "valves only", "item_count": 0},
        {"layer_id": "equipment_only", "label": "equipment only", "item_count": 0},
        {"layer_id": "boundaries_only", "label": "boundaries only", "item_count": len(boundaries)},
        {"layer_id": "vacuum_barrier", "label": "vacuum barrier", "item_count": sum(1 for b in boundaries if "vacuum" in str(b).lower())},
        {"layer_id": "qm_section", "label": "QM section", "item_count": subsystem_counts.get("QM section", 0)},
        {"layer_id": "jumper_section", "label": "Jumper section", "item_count": subsystem_counts.get("Jumper section", 0)},
        {"layer_id": "qvb_section", "label": "QVB section", "item_count": subsystem_counts.get("QVB section", 0)},
        {"layer_id": "qinfra_interface_section", "label": "QINFRA/interface section", "item_count": subsystem_counts.get("QINFRA/interface section", 0)},
        {"layer_id": "arrows_flow_direction", "label": "arrows / flow direction only", "item_count": len(arrows)},
        {"layer_id": "unresolved_items", "label": "unresolved items", "item_count": len(unresolved_arrows)+len(unresolved_colours)+len(unresolved_tags)},
    ]
    semantic_layer_model = {"schema_version": "0.1", **run, "layers": layers}
    subsystem_model = {"schema_version": "0.1", **run, "subsystems": [{"subsystem": k, "item_count": v} for k, v in sorted(subsystem_counts.items())]}
    tag_register = {"schema_version": "0.1", **run, "summary": {"tag_count": len(tags), "tag_counts": dict(tag_counts), "unresolved_tag_count": len(unresolved_tags)}, "tags": tags, "boundaries": boundaries}

    write_json(MODEL_DIR / "line_model.json", line_model)
    write_json(MODEL_DIR / "semantic_layer_model.json", semantic_layer_model)
    write_json(MODEL_DIR / "subsystem_model.json", subsystem_model)
    write_json(MODEL_DIR / "arrow_direction_model.json", arrow_model)
    write_json(MODEL_DIR / "tag_layer_register.json", tag_register)
    for bin_id, filename in LINE_BIN_FILES.items():
        write_json(LINES_DIR / filename, {"schema_version": "0.1", **run, "colour_bin": bin_id, "line_count": colour_counts.get(bin_id, 0), "lines": [l for l in lines if l["colour_bin"] == bin_id]})

    reports = build_reports(run, colour_counts, arrow_colour_counts, tag_counts, subsystem_counts, lines, arrows, tags, boundaries, unresolved_arrows, unresolved_colours, unresolved_tags, layers)
    for name, body in reports.items():
        (REPORTS_DIR / name).write_text(body, encoding="utf-8")
    write_html(found_inputs, lines, arrows, tags, boundaries, layers, unresolved_arrows, unresolved_colours, unresolved_tags)
    return {"found_inputs": found_inputs, "missing_inputs": missing_inputs, "layers": layers, "subsystems": dict(subsystem_counts), "arrow_counts": dict(arrow_colour_counts), "unresolved": {"arrows": len(unresolved_arrows), "colours": len(unresolved_colours), "tags": len(unresolved_tags)}}


def build_reports(run, colour_counts, arrow_colour_counts, tag_counts, subsystem_counts, lines, arrows, tags, boundaries, unresolved_arrows, unresolved_colours, unresolved_tags, layers):
    found_rows = [[i["path"], i["kind"], i["size_bytes"]] for i in run["inputs_found"]] or [["No required real input files found", "n/a", 0]]
    load_rows = [[s["path"], s["status"], s.get("error") or ""] for s in run["svg_load_status"]]
    colour_rows = [[k, v] for k, v in sorted(colour_counts.items())] or [["none", 0]]
    arrow_rows = [[k, v] for k, v in sorted(arrow_colour_counts.items())] or [["none", 0]]
    tag_rows = [[k, v] for k, v in sorted(tag_counts.items())] or [["none", 0]]
    subsys_rows = [[k, v] for k, v in sorted(subsystem_counts.items())] or [["none", 0]]
    common = f"""## Actual input files found\n{markdown_table(found_rows, ['path','kind','size_bytes'])}\n\n## SVG load status\n{markdown_table(load_rows, ['path','status','error'])}\n\n## Colour bins detected\n{markdown_table(colour_rows, ['colour_bin','path_line_count'])}\n\n## Arrow counts per colour\n{markdown_table(arrow_rows, ['colour_bin','arrow_count'])}\n\n## Tag counts\n{markdown_table(tag_rows, ['tag_class','count'])}\n\n## Subsystem counts\n{markdown_table(subsys_rows, ['subsystem','count'])}\n\n## Boundary counts\n- Boundaries detected: {len(boundaries)}\n\n## Unresolved counts\n- Unresolved arrows: {len(unresolved_arrows)}\n- Unresolved colours: {len(unresolved_colours)}\n- Unresolved tags: {len(unresolved_tags)}\n\n## Confidence notes\n- Colour/process mappings are bin-level hypotheses from SVG stroke colour only.\n- Arrow direction is only inferred for SVG marker evidence with available endpoints; geometric arrow-head candidates remain unresolved.\n- Subsystem assignment requires visible text evidence or a conservative nearest-label association.\n\n## Known gaps\n- PPTX inputs are inventoried for traceability but not parsed in this W003 preparation step.\n- Valve/equipment symbol classification remains conservative until symbol templates are supplied.\n- If the real SVG files are absent, generated models intentionally contain no inferred process semantics.\n"""
    return {
        "W002_colour_line_validation.md": "# W002 Colour Line Validation\n\n" + common + f"\n## Unresolved colours\n{markdown_table([[l['line_id'], l['source_file'], l['source_colour'], l['unresolved_reason']] for l in unresolved_colours[:50]] or [['none','','','']], ['line_id','source_file','colour','reason'])}\n",
        "W003_semantic_layer_validation.md": "# W003 Semantic Layer Validation\n\n" + common + f"\n## Semantic layers\n{markdown_table([[x['layer_id'], x['label'], x['item_count']] for x in layers], ['layer_id','label','count'])}\n",
        "W003_arrow_direction_validation.md": "# W003 Arrow Direction Validation\n\n" + common + f"\n## Unresolved arrows\n{markdown_table([[a['arrow_id'], a['source_file'], a.get('source_colour'), a.get('line_id') or '', a.get('unresolved_reason') or ''] for a in unresolved_arrows[:100]] or [['none','','','','']], ['arrow_id','source_file','colour','line_id','reason'])}\n",
    }


def write_html(found_inputs, lines, arrows, tags, boundaries, layers, unresolved_arrows, unresolved_colours, unresolved_tags):
    svg_src = found_inputs[0]["path"] if found_inputs and found_inputs[0]["kind"] == "svg" else "../data/svg/PFD-PID MINERVA QCELL-LB.svg"
    data = {"lines": lines, "arrows": arrows, "tags": tags, "boundaries": boundaries, "layers": layers, "unresolved": {"arrows": unresolved_arrows, "colours": unresolved_colours, "tags": unresolved_tags}, "svg_src": svg_src}
    js_data = json.dumps(data)
    html = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>ABACUS P&amp;ID Semantic Viewer</title>
<style>
@page {{ size: A3 landscape; margin: 8mm; }}
:root {{ --panel:#14213d; --accent:#fca311; --paper:#f7f7f7; }}
body {{ margin:0; font-family: system-ui, sans-serif; background:#111; color:#eee; }}
.app {{ display:grid; grid-template-columns: 340px 1fr 320px; min-height:100vh; }}
aside {{ background:var(--panel); padding:1rem; overflow:auto; }}
main {{ background:var(--paper); color:#111; overflow:auto; position:relative; }}
button,label,input {{ font:inherit; }}
.toggle {{ display:block; margin:.25rem 0; padding:.25rem; border-bottom:1px solid rgba(255,255,255,.1); }}
#canvas {{ position:relative; min-height:80vh; padding:1rem; }}
#svgHost svg {{ max-width:100%; height:auto; background:white; }}
.overlay {{ position:absolute; left:1rem; top:1rem; pointer-events:none; }}
.meta {{ white-space:pre-wrap; font-family: ui-monospace, monospace; font-size:12px; }}
.badge {{ display:inline-block; border:1px solid currentColor; border-radius:999px; padding:.1rem .4rem; margin:.1rem; }}
.line-label {{ background:white; color:#111; border:1px solid #111; font-size:11px; padding:1px 3px; }}
@media print {{ body {{ background:white; color:black; }} .app {{ display:block; }} aside {{ display:none; }} main {{ overflow:visible; }} }}
</style></head><body><div class="app">
<aside><h1>P&amp;ID Viewer</h1><p>Original SVG is preserved; semantic overlays are toggleable and conservative.</p><input id="search" placeholder="Search by tag" style="width:100%"><h2>Toggles</h2><div id="toggles"></div></aside>
<main><div id="canvas"><div id="svgHost"></div><svg id="overlay" class="overlay"></svg></div></main>
<aside><h2>Metadata</h2><div id="meta" class="meta">Click an overlay item.</div><h2>Unresolved items</h2><div id="unresolved"></div></aside>
</div><script>
const MODEL = {js_data};
const active = new Set(MODEL.layers.map(l => l.layer_id));
const toggles = document.getElementById('toggles');
for (const layer of MODEL.layers) {{
  const label = document.createElement('label'); label.className='toggle';
  label.innerHTML = `<input type="checkbox" checked data-layer="${{layer.layer_id}}"> ${{layer.label}} <span class="badge">${{layer.item_count}}</span>`;
  toggles.appendChild(label);
}}
toggles.addEventListener('change', e => {{ if (!e.target.dataset.layer) return; e.target.checked ? active.add(e.target.dataset.layer) : active.delete(e.target.dataset.layer); renderOverlay(); }});
document.getElementById('search').addEventListener('input', renderOverlay);
fetch(MODEL.svg_src).then(r => r.ok ? r.text() : Promise.reject(new Error(r.status + ' ' + r.statusText))).then(txt => {{ document.getElementById('svgHost').innerHTML = txt; sizeOverlay(); renderOverlay(); }}).catch(err => {{ document.getElementById('svgHost').innerHTML = `<div style="padding:2rem;background:white;border:2px dashed #999">SVG input unavailable: ${{MODEL.svg_src}}<br>${{err.message}}</div>`; renderOverlay(); }});
window.addEventListener('resize', () => {{ sizeOverlay(); renderOverlay(); }});
function sizeOverlay() {{ const svg = document.querySelector('#svgHost svg'); const ov = document.getElementById('overlay'); if (svg) {{ const b=svg.getBoundingClientRect(); ov.setAttribute('width', b.width); ov.setAttribute('height', b.height); }} }}
function show(item) {{ document.getElementById('meta').textContent = JSON.stringify(item, null, 2); }}
function visible(item) {{ const ids = item.viewer_layer_ids || []; return active.has('full_drawing') || ids.some(x => active.has(x)); }}
function renderOverlay() {{
  const ov = document.getElementById('overlay'); ov.innerHTML=''; const q=document.getElementById('search').value.toLowerCase();
  for (const line of MODEL.lines) {{ if (!visible(line)) continue; drawBox(ov,line,line.source_colour||'black','4 2'); }}
  for (const b of MODEL.boundaries) {{ if (!active.has('boundaries_only') && !active.has('full_drawing')) continue; drawBox(ov,b,'#7b2cbf','8 4'); }}
  for (const a of MODEL.arrows) {{ if (!active.has('arrows_flow_direction') && !active.has('full_drawing')) continue; drawArrow(ov,a); }}
  for (const t of MODEL.tags) {{ if (q && !t.text.toLowerCase().includes(q)) continue; if (!active.has('instruments_only') && !active.has('full_drawing')) continue; drawText(ov,t); }}
  renderUnresolved();
}}
function drawBox(ov,item,color,dash) {{ if(!item.bbox) return; const r=document.createElementNS('http://www.w3.org/2000/svg','rect'); const b=item.bbox; r.setAttribute('x',b.x_min); r.setAttribute('y',b.y_min); r.setAttribute('width',Math.max(2,b.x_max-b.x_min)); r.setAttribute('height',Math.max(2,b.y_max-b.y_min)); r.setAttribute('fill','none'); r.setAttribute('stroke',color); r.setAttribute('stroke-width','2'); r.setAttribute('stroke-dasharray',dash); r.style.pointerEvents='all'; r.addEventListener('click',()=>show(item)); ov.appendChild(r); }}
function drawArrow(ov,a) {{ const p=a.arrow_tip_coordinate, s=a.start_body_coordinate; if(!p) return; const c=a.confidence>=0.7?'#d00000':'#ffba08'; const g=document.createElementNS('http://www.w3.org/2000/svg','g'); const circ=document.createElementNS('http://www.w3.org/2000/svg','circle'); circ.setAttribute('cx',p[0]); circ.setAttribute('cy',p[1]); circ.setAttribute('r','5'); circ.setAttribute('fill',c); g.appendChild(circ); if(s) {{ const line=document.createElementNS('http://www.w3.org/2000/svg','line'); line.setAttribute('x1',s[0]); line.setAttribute('y1',s[1]); line.setAttribute('x2',p[0]); line.setAttribute('y2',p[1]); line.setAttribute('stroke',c); line.setAttribute('stroke-width','2'); g.appendChild(line); }} g.style.pointerEvents='all'; g.addEventListener('click',()=>show(a)); ov.appendChild(g); }}
function drawText(ov,t) {{ const el=document.createElementNS('http://www.w3.org/2000/svg','text'); el.setAttribute('x',t.coordinate[0]); el.setAttribute('y',t.coordinate[1]); el.setAttribute('class','line-label'); el.textContent=t.text.slice(0,28); el.style.pointerEvents='all'; el.addEventListener('click',()=>show(t)); ov.appendChild(el); }}
function renderUnresolved() {{ const u=document.getElementById('unresolved'); u.innerHTML=''; for (const [kind,items] of Object.entries(MODEL.unresolved)) {{ const h=document.createElement('h3'); h.textContent=`${{kind}} (${{items.length}})`; u.appendChild(h); for (const item of items.slice(0,40)) {{ const d=document.createElement('button'); d.textContent=item.arrow_id||item.line_id||item.tag_id||'unresolved'; d.onclick=()=>show(item); u.appendChild(d); u.appendChild(document.createElement('br')); }} }} }}
</script></body></html>'''
    (VIEWER_DIR / "index.html").write_text(html, encoding="utf-8")
    (PUBLISH_DIR / "colour_line_collage.html").write_text(html.replace("P&amp;ID Semantic Viewer", "Colour Line Collage"), encoding="utf-8")


if __name__ == "__main__":
    result = build_models()
    print(json.dumps(result, indent=2))
