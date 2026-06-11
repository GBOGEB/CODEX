#!/usr/bin/env python3
"""Build conservative P&ID SVG semantic models from local repository assets only."""
from __future__ import annotations

import argparse
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
SVG_ROOT = ROOT / "data/svg"
PDF_ROOT = ROOT / "data/pdf"
PPT_ROOT = ROOT / "data/ppt"
MODEL_DIR = ROOT / "data/model"
LINES_DIR = MODEL_DIR / "lines"
REPORTS_DIR = ROOT / "reports"
VIEWER_DIR = ROOT / "viewer"
PUBLISH_DIR = ROOT / "publish"
SUBSYSTEMS = ["QM", "Jumper", "QVB", "QINFRA", "Unknown"]
BIN_FILES = {
    "blue_A": "blue_A.json",
    "cyan_B_2K": "cyan_B_2K.json",
    "green_W_coupler": "green_W_coupler.json",
    "grey_V_vent": "grey_V_vent.json",
    "olive_S_line": "olive_S_line.json",
    "red_orange_D_E": "red_orange_D_E.json",
    "unknown_black_or_other": "unknown_black_or_other.json",
}

NS_RE = re.compile(r"^\{.*\}")
NUM_RE = re.compile(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?")
STYLE_RE = re.compile(r"\s*;\s*")
TRANS_RE = re.compile(r"translate\(([-+]?\d*\.?\d+)(?:[,\s]+([-+]?\d*\.?\d+))?")
TAG_RE = re.compile(r"\b(?:[A-Z]{1,8}[-_ ]?)?\d{2,}[A-Z0-9_.-]*\b|\b(?:QM|QVB|QINFRA|JUMPER|RFCELL|QCELL|ACR)\b", re.I)
VALVE_RE = re.compile(r"\b(?:V|HV|CV|XV|PV|SV|MOV|EV)[-_ ]?\d+", re.I)
INSTR_RE = re.compile(r"\b(?:TT|TE|PT|PI|PIC|FT|FI|FIC|LT|LI|LIT|TS|PS|LS|PDT|AIT)[-_ ]?\d+", re.I)
EQUIP_RE = re.compile(r"\b(?:HX|PUMP|COMP|DEWAR|VESSEL|TANK|CELL|QVB|QM|JUMPER|RFCELL|QCELL)\b", re.I)
CSS_CLASS_RE = re.compile(r"\.([A-Za-z0-9_-]+)\s*\{([^}]*)\}")


class MissingLocalAssets(RuntimeError):
    """Raised when local SVG assets required for extraction are absent."""


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def strip_ns(tag: str) -> str:
    return NS_RE.sub("", tag)


def parse_style(value: str | None) -> dict[str, str]:
    out: dict[str, str] = {}
    for part in STYLE_RE.split((value or "").strip()):
        if ":" in part:
            key, val = part.split(":", 1)
            out[key.strip().lower()] = val.strip()
    return out





def mx_style(value: str | None) -> dict[str, str]:
    out: dict[str, str] = {}
    for part in (value or "").split(";"):
        if "=" in part:
            key, val = part.split("=", 1)
            out[key.strip()] = val.strip()
    return out


def mx_geometry(cell: ET.Element) -> dict[str, float] | None:
    for child in cell:
        if strip_ns(child.tag) == "mxGeometry":
            x = float(child.attrib.get("x", 0) or 0)
            y = float(child.attrib.get("y", 0) or 0)
            width = float(child.attrib.get("width", 0) or 0)
            height = float(child.attrib.get("height", 0) or 0)
            return {"x_min": x, "y_min": y, "x_max": x + width, "y_max": y + height}
    return None


def html_text(value: str | None) -> str:
    return re.sub(r"<[^>]+>", " ", value or "").replace("&nbsp;", " ").strip()

def svg_attr(element: ET.Element, name: str, class_styles: dict[str, dict[str, str]] | None = None) -> str | None:
    direct = element.attrib.get(name) or parse_style(element.attrib.get("style")).get(name)
    if direct:
        return direct
    for class_name in (element.attrib.get("class") or "").split():
        value = (class_styles or {}).get(class_name, {}).get(name)
        if value:
            return value
    return None


def collect_class_styles(root: ET.Element) -> dict[str, dict[str, str]]:
    class_styles: dict[str, dict[str, str]] = {}
    for element in root.iter():
        if strip_ns(element.tag) == "style":
            css = "".join(element.itertext())
            for class_name, declarations in CSS_CLASS_RE.findall(css):
                class_styles[class_name] = parse_style(declarations)
    return class_styles


def norm_colour(value: str | None) -> str:
    if not value:
        return "none"
    value = value.strip().lower()
    names = {
        "black": "#000000",
        "white": "#ffffff",
        "blue": "#0000ff",
        "cyan": "#00ffff",
        "aqua": "#00ffff",
        "green": "#008000",
        "grey": "#808080",
        "gray": "#808080",
        "olive": "#808000",
        "red": "#ff0000",
        "orange": "#ffa500",
        "none": "none",
    }
    if value in names:
        return names[value]
    if value.startswith("#"):
        return "#" + "".join(ch * 2 for ch in value[1:]) if len(value) == 4 else value[:7]
    rgb_match = re.match(r"rgba?\(([^)]+)\)", value)
    if rgb_match:
        vals = [float(x.strip().rstrip("%")) for x in rgb_match.group(1).split(",")[:3]]
        if "%" in rgb_match.group(1):
            vals = [x * 2.55 for x in vals]
        return "#" + "".join(f"{max(0, min(255, round(x))):02x}" for x in vals)
    return value


def rgb_tuple(colour: str) -> tuple[int, int, int] | None:
    if re.match(r"^#[0-9a-f]{6}$", colour):
        return int(colour[1:3], 16), int(colour[3:5], 16), int(colour[5:7], 16)
    return None


def bin_colour(colour: str) -> tuple[str, str, float]:
    rgb = rgb_tuple(norm_colour(colour))
    if not rgb:
        return "unknown_black_or_other", "unknown/other", 0.2
    red, green, blue = rgb
    if red < 45 and green < 45 and blue < 45:
        return "unknown_black_or_other", "structure/unknown", 0.55
    if blue > 120 and red < 120 and green < 170:
        return "blue_A", "A / A′", 0.78
    if blue > 130 and green > 130 and red < 120:
        return "cyan_B_2K", "B / B′", 0.78
    if green > 100 and red < 120 and blue < 130:
        return "green_W_coupler", "W", 0.72
    if abs(red - green) < 25 and abs(green - blue) < 25 and 70 <= red <= 210:
        return "grey_V_vent", "V", 0.68
    if red > 80 and green > 80 and blue < 100 and abs(red - green) < 80:
        return "olive_S_line", "S", 0.68
    if red > 150 and green < 180 and blue < 130:
        return "red_orange_D_E", "D/E", 0.72
    return "unknown_black_or_other", "unknown/other", 0.35


def nums(value: str | None) -> list[float]:
    return [float(x) for x in NUM_RE.findall(value or "")]


def points(element: ET.Element) -> list[tuple[float, float]]:
    tag = strip_ns(element.tag)
    if tag == "line" and all(k in element.attrib for k in ("x1", "y1", "x2", "y2")):
        return [(float(element.attrib["x1"]), float(element.attrib["y1"])), (float(element.attrib["x2"]), float(element.attrib["y2"]))]
    if tag in {"polyline", "polygon"}:
        values = nums(element.attrib.get("points"))
        return list(zip(values[0::2], values[1::2]))
    if tag == "path":
        values = nums(element.attrib.get("d"))
        return list(zip(values[0::2], values[1::2]))
    if tag == "rect":
        x, y, w, h = map(float, [element.attrib.get("x", 0), element.attrib.get("y", 0), element.attrib.get("width", 0), element.attrib.get("height", 0)])
        return [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
    if tag in {"circle", "ellipse"}:
        cx, cy = float(element.attrib.get("cx", 0)), float(element.attrib.get("cy", 0))
        rx = float(element.attrib.get("r", element.attrib.get("rx", 0)))
        ry = float(element.attrib.get("r", element.attrib.get("ry", 0)))
        return [(cx - rx, cy - ry), (cx + rx, cy + ry)]
    return []


def bbox(point_list: list[tuple[float, float]]) -> dict[str, float] | None:
    if not point_list:
        return None
    xs = [p[0] for p in point_list]
    ys = [p[1] for p in point_list]
    return {"x_min": min(xs), "y_min": min(ys), "x_max": max(xs), "y_max": max(ys)}


def center(box: dict[str, float] | None) -> tuple[float, float] | None:
    if not box:
        return None
    return (statistics.mean([box["x_min"], box["x_max"]]), statistics.mean([box["y_min"], box["y_max"]]))


def distance(a: tuple[float, float], b: tuple[float, float]) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def infer_subsystem_match(text: str) -> tuple[str, str | None]:
    upper = text.upper()
    if "QINFRA" in upper or "INTERFACE" in upper:
        return "QINFRA", "QINFRA/interface label token"
    if "JUMPER" in upper or "JT VALVE" in upper:
        return "Jumper", "Jumper/JT Valve label token"
    if "QVB" in upper or "VACUUM" in upper:
        return "QVB", "QVB/vacuum label token"
    if "QM" in upper:
        return "QM", "QM label token"
    qinfra_tokens = [
        "PRESSURE", "DIAGNOSTIC", "QSYS", "QPS", "QPLANT", "WCS", "QRB", "WSH", "QSN",
        "SUPPLY PRESSURE", "RETURN PRESSURE", "ΔP", "DP DIAGNOSTIC",
    ]
    for token in qinfra_tokens:
        if token in upper:
            return "QINFRA", f"QINFRA label token: {token}"
    qm_tokens = [
        "QCELL", "THERMAL", "2 K", "4 K", "30 K", "50 K", "60 K", "77 K",
        "HE II", "HEAT EXCHANGER", "SUPERFLUID", "COOLANT", "HEAT LOAD", "CRYOGENIC", "TEMPERATURE", "WARM EXTENSION",
    ]
    for token in qm_tokens:
        if token in upper:
            return "QM", f"QM label token: {token}"
    return "Unknown", None


def infer_subsystem(text: str) -> str:
    return infer_subsystem_match(text)[0]

def classify_tag(text: str) -> tuple[str, list[str]]:
    classes: list[str] = []
    if INSTR_RE.search(text):
        classes.append("instrument")
    if VALVE_RE.search(text):
        classes.append("valve")
    if EQUIP_RE.search(text):
        classes.append("equipment")
    if not classes and TAG_RE.search(text):
        classes.append("tag")
    return (classes[0] if classes else "annotation_or_label"), classes


def discover_local_assets() -> dict[str, list[dict[str, Any]]]:
    return {
        "svg": [{"path": rel(path), "size_bytes": path.stat().st_size, "kind": "svg"} for path in sorted(SVG_ROOT.glob("**/*.svg"))],
        "pdf": [{"path": rel(path), "size_bytes": path.stat().st_size, "kind": "pdf"} for path in sorted(PDF_ROOT.glob("**/*.pdf"))],
        "ppt": [{"path": rel(path), "size_bytes": path.stat().st_size, "kind": "pptx"} for path in sorted(PPT_ROOT.glob("**/*.pptx"))],
    }



def parse_drawio_cells(root: ET.Element, path: Path, index: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    lines: list[dict[str, Any]] = []
    arrows: list[dict[str, Any]] = []
    tags: list[dict[str, Any]] = []
    boundaries: list[dict[str, Any]] = []
    for diagram_index, diagram in enumerate([e for e in root.iter() if strip_ns(e.tag) == "diagram"], 1):
        diagram_id = diagram.attrib.get("id") or f"diagram_{diagram_index}"
        cells = [e for e in diagram.iter() if strip_ns(e.tag) == "mxCell"]
        cell_map = {cell.attrib.get("id", f"cell_{i}"): cell for i, cell in enumerate(cells)}
        centers: dict[str, tuple[float, float]] = {}
        cell_subsystems: dict[str, str] = {}
        cell_values: dict[str, str] = {}
        cell_rules: dict[str, str | None] = {}
        for cell_id, cell in cell_map.items():
            if cell.attrib.get("vertex") != "1":
                continue
            value = html_text(cell.attrib.get("value"))
            box = mx_geometry(cell)
            if box:
                centers[cell_id] = center(box) or (0.0, 0.0)
            if not value:
                continue
            semantic_class, classes = classify_tag(value)
            subsystem, subsystem_rule = infer_subsystem_match(value)
            cell_values[cell_id] = value
            cell_subsystems[cell_id] = subsystem
            cell_rules[cell_id] = subsystem_rule
            coordinate = list(centers.get(cell_id, (0.0, 0.0)))
            tags.append({
                "tag_id": f"tag_{index:02d}_mx_{diagram_index}_{len(tags) + 1:05d}",
                "source_file": rel(path),
                "source_svg_id": f"{diagram_id}:{cell_id}",
                "text": value,
                "detected_tokens": TAG_RE.findall(value),
                "coordinate": coordinate,
                "semantic_class": semantic_class,
                "semantic_classes": classes,
                "subsystem": subsystem,
                "confidence": 0.82 if TAG_RE.search(value) else 0.45,
                "subsystem_rule": subsystem_rule,
                "evidence": ["draw.io mxCell value"] + ([f"subsystem rule: {subsystem_rule}"] if subsystem_rule else []),
                "unresolved_reason": None if subsystem != "Unknown" or TAG_RE.search(value) else "Draw.io label does not match tag/subsystem regex.",
            })
            style = mx_style(cell.attrib.get("style"))
            if box and (style.get("swimlane") is not None or (box["x_max"] - box["x_min"] > 100 and box["y_max"] - box["y_min"] > 80)):
                boundaries.append({
                    "boundary_id": f"boundary_{index:02d}_mx_{diagram_index}_{len(boundaries) + 1:05d}",
                    "source_file": rel(path),
                    "source_svg_id": f"{diagram_id}:{cell_id}",
                    "label": value,
                    "bbox": box,
                    "stroke": norm_colour(style.get("strokeColor")),
                    "subsystem": subsystem,
                    "subsystem_rule": subsystem_rule,
                    "confidence": 0.62 if subsystem != "Unknown" else 0.46,
                    "evidence": ["draw.io vertex geometry", "swimlane/large cell boundary"],
                    "unresolved_reason": None if subsystem != "Unknown" else "Boundary label is not one of QM/Jumper/QVB/QINFRA.",
                })
        for cell_id, cell in cell_map.items():
            if cell.attrib.get("edge") != "1":
                continue
            style = mx_style(cell.attrib.get("style"))
            source = cell.attrib.get("source")
            target = cell.attrib.get("target")
            source_point = centers.get(source or "")
            target_point = centers.get(target or "")
            if not source_point or not target_point:
                continue
            stroke = norm_colour(style.get("strokeColor") or "#000000")
            colour_bin, process, confidence = bin_colour(stroke)
            line_id = f"line_{index:02d}_mx_{diagram_index}_{len(lines) + 1:05d}"
            source_label = cell_values.get(source or "", "")
            target_label = cell_values.get(target or "", "")
            source_subsystem = cell_subsystems.get(source or "", "Unknown")
            target_subsystem = cell_subsystems.get(target or "", "Unknown")
            subsystem = source_subsystem if source_subsystem != "Unknown" else target_subsystem
            subsystem_rule = cell_rules.get(source or "") if source_subsystem != "Unknown" else cell_rules.get(target or "")
            line = {
                "line_id": line_id,
                "source_file": rel(path),
                "source_svg_id": f"{diagram_id}:{cell_id}",
                "source_colour": stroke,
                "colour_bin": colour_bin,
                "process": process,
                "geometry": {"points_sample": [source_point, target_point], "bbox": bbox([source_point, target_point])},
                "source_endpoint_labels": {"source": source_label, "target": target_label},
                "subsystem": subsystem or "Unknown",
                "subsystem_rule": subsystem_rule,
                "confidence": confidence,
                "evidence": ["draw.io mxCell edge", f"source={source}", f"target={target}", f"source label={source_label}", f"target label={target_label}", f"stroke={stroke}"] + ([f"subsystem rule: {subsystem_rule}"] if subsystem_rule else []),
                "unresolved_reason": None if colour_bin != "unknown_black_or_other" else "Colour maps to black/unknown/structure pending validation.",
            }
            lines.append(line)
            arrow_style = style.get("endArrow") or style.get("startArrow")
            if arrow_style and arrow_style.lower() != "none":
                tip = target_point if style.get("endArrow") else source_point
                body = source_point if style.get("endArrow") else target_point
                arrows.append({
                    "arrow_id": f"arrow_{index:02d}_mx_{diagram_index}_{len(arrows) + 1:05d}",
                    "source_file": rel(path),
                    "source_svg_id": f"{diagram_id}:{cell_id}",
                    "source_colour": stroke,
                    "arrow_body_geometry": {"coordinate": body},
                    "arrow_tip_geometry": {"coordinate": tip},
                    "direction_vector": [tip[0] - body[0], tip[1] - body[1]],
                    "associated_line_id": line_id,
                    "associated_subsystem": line["subsystem"],
                    "source_endpoint_labels": {"source": source_label, "target": target_label},
                    "subsystem_rule": subsystem_rule,
                    "confidence": 0.82,
                    "evidence": ["draw.io mxCell endArrow/startArrow evidence", f"arrow={arrow_style}", f"source={source}", f"target={target}", f"source label={source_label}", f"target label={target_label}"] + ([f"subsystem rule: {subsystem_rule}"] if subsystem_rule else []),
                    "unresolved_reason": None,
                })
    return lines, arrows, tags, boundaries


def parse_svg(path: Path, index: int) -> dict[str, Any]:
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as exc:
        return {"path": rel(path), "status": "load_error", "error": str(exc), "lines": [], "arrows": [], "tags": [], "boundaries": []}

    class_styles = collect_class_styles(root)
    lines: list[dict[str, Any]] = []
    arrows: list[dict[str, Any]] = []
    tags: list[dict[str, Any]] = []
    boundaries: list[dict[str, Any]] = []
    for elem_index, element in enumerate(root.iter()):
        tag = strip_ns(element.tag)
        source_svg_id = element.attrib.get("id") or f"svg{index}_{tag}_{elem_index}"
        stroke = norm_colour(svg_attr(element, "stroke", class_styles))
        fill = norm_colour(svg_attr(element, "fill", class_styles))
        point_list = points(element)
        box = bbox(point_list)
        style = parse_style(element.attrib.get("style"))

        if tag in {"path", "line", "polyline"} and stroke not in {"none", "#ffffff"} and point_list:
            colour_bin, process, confidence = bin_colour(stroke)
            line_id = f"line_{index:02d}_{len(lines) + 1:05d}"
            unresolved = None if colour_bin != "unknown_black_or_other" else "Colour maps to black/unknown/structure pending validation."
            lines.append({
                "line_id": line_id,
                "source_file": rel(path),
                "source_svg_id": source_svg_id,
                "source_colour": stroke,
                "colour_bin": colour_bin,
                "process": process,
                "geometry": {"points_sample": point_list[:20], "bbox": box},
                "subsystem": "Unknown",
                "confidence": confidence,
                "evidence": [f"stroke={stroke}", f"element={tag}"],
                "unresolved_reason": unresolved,
            })
            marker_end = element.attrib.get("marker-end") or style.get("marker-end")
            marker_start = element.attrib.get("marker-start") or style.get("marker-start")
            if marker_end or marker_start:
                tip = point_list[-1] if marker_end else point_list[0]
                body = point_list[0] if marker_end else point_list[-1]
                arrows.append({
                    "arrow_id": f"arrow_{index:02d}_{len(arrows) + 1:05d}",
                    "source_file": rel(path),
                    "source_svg_id": source_svg_id,
                    "source_colour": stroke,
                    "arrow_body_geometry": {"coordinate": body},
                    "arrow_tip_geometry": {"coordinate": tip},
                    "direction_vector": [tip[0] - body[0], tip[1] - body[1]],
                    "associated_line_id": line_id,
                    "associated_subsystem": "Unknown",
                    "confidence": 0.84,
                    "evidence": ["SVG marker-start/marker-end evidence", f"marker={marker_end or marker_start}"],
                    "unresolved_reason": None,
                })

        if tag == "path" and point_list and fill not in {"none", "#ffffff"} and len(point_list) >= 3:
            arrow_box = bbox(point_list[:4])
            if arrow_box and arrow_box["x_max"] - arrow_box["x_min"] <= 40 and arrow_box["y_max"] - arrow_box["y_min"] <= 40:
                arrows.append({
                    "arrow_id": f"arrow_{index:02d}_{len(arrows) + 1:05d}",
                    "source_file": rel(path),
                    "source_svg_id": source_svg_id,
                    "source_colour": fill,
                    "arrow_body_geometry": None,
                    "arrow_tip_geometry": {"coordinate": point_list[0]},
                    "direction_vector": None,
                    "associated_line_id": None,
                    "associated_subsystem": "Unknown",
                    "confidence": 0.38,
                    "evidence": ["Small filled path resembles possible arrow head", "No connected body line proven"],
                    "unresolved_reason": "Possible arrow head is not confidently associated with a body line; direction not inferred.",
                })

        if tag == "text":
            text = "".join(element.itertext()).strip()
            if text:
                transform = TRANS_RE.search(element.attrib.get("transform", ""))
                x_coord = float(element.attrib.get("x", transform.group(1) if transform else 0) or 0)
                y_coord = float(element.attrib.get("y", transform.group(2) if transform and transform.group(2) else 0) or 0)
                semantic_class, classes = classify_tag(text)
                inferred_subsystem, subsystem_rule = infer_subsystem_match(text)
                tags.append({
                    "tag_id": f"tag_{index:02d}_{len(tags) + 1:05d}",
                    "source_file": rel(path),
                    "source_svg_id": source_svg_id,
                    "text": text,
                    "detected_tokens": TAG_RE.findall(text),
                    "coordinate": [x_coord, y_coord],
                    "semantic_class": semantic_class,
                    "semantic_classes": classes,
                    "subsystem": inferred_subsystem,
                    "subsystem_rule": subsystem_rule,
                    "confidence": 0.82 if TAG_RE.search(text) else (0.7 if inferred_subsystem != "Unknown" else 0.45),
                    "evidence": ["SVG text element"] + ([f"subsystem rule: {subsystem_rule}"] if subsystem_rule else []),
                    "unresolved_reason": None if inferred_subsystem != "Unknown" or TAG_RE.search(text) else "Text could not be classified as a tag by conservative regex.",
                })

        dashed = element.attrib.get("stroke-dasharray") or style.get("stroke-dasharray")
        if tag in {"rect", "polygon", "polyline", "path"} and box and (dashed or tag == "rect") and box["x_max"] - box["x_min"] > 100 and box["y_max"] - box["y_min"] > 80:
            boundaries.append({
                "boundary_id": f"boundary_{index:02d}_{len(boundaries) + 1:05d}",
                "source_file": rel(path),
                "source_svg_id": source_svg_id,
                "bbox": box,
                "stroke": stroke,
                "subsystem": "Unknown",
                "confidence": 0.5,
                "evidence": ["large enclosing geometry"],
                "unresolved_reason": "Boundary/scope label not directly associated.",
            })

    # Do not resolve unlabeled SVG geometry by proximity alone; subsystem assignment
    # must be backed by direct label text or explicit draw.io endpoint labels.
    line_map = {line["line_id"]: line for line in lines}
    for arrow in arrows:
        line = line_map.get(arrow.get("associated_line_id"))
        if line:
            arrow["associated_subsystem"] = line["subsystem"]
    mx_lines, mx_arrows, mx_tags, mx_boundaries = parse_drawio_cells(root, path, index)
    lines.extend(mx_lines)
    arrows.extend(mx_arrows)
    tags.extend(mx_tags)
    boundaries.extend(mx_boundaries)
    return {"path": rel(path), "status": "loaded", "lines": lines, "arrows": arrows, "tags": tags, "boundaries": boundaries}


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def markdown_table(rows: list[list[Any]], headers: list[str]) -> str:
    return "| " + " | ".join(headers) + " |\n| " + " | ".join(["---"] * len(headers)) + " |\n" + "\n".join("| " + " | ".join(map(str, row)) + " |" for row in rows)


def ensure_local_svg_assets(assets: dict[str, list[dict[str, Any]]]) -> None:
    if assets["svg"]:
        return
    payload = {
        "status": "MISSING_LOCAL_ASSETS",
        "message": "No local SVG assets found; extraction stopped before generating models, reports, or viewer files.",
        "discovered_local_assets": assets,
        "validation_status": "failed_svg_count_0",
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    raise MissingLocalAssets("MISSING_LOCAL_ASSETS")



def unknown_resolution_diagnostics(lines: list[dict[str, Any]], arrows: list[dict[str, Any]], tags: list[dict[str, Any]], boundaries: list[dict[str, Any]]) -> dict[str, Any]:
    """Group Unknown objects by the primary evidence gap blocking subsystem resolution."""
    rows: list[list[Any]] = []
    counts = {
        "no_matching_pattern_in_tag_layer_register": 0,
        "outside_all_resolved_boundaries": 0,
        "no_tag_or_label": 0,
    }
    resolved_boundaries = [item for item in boundaries if item.get("subsystem") not in {None, "Unknown"}]

    def add(object_type: str, object_id: str, item: dict[str, Any], label: str, reason: str, category: str) -> None:
        counts[category] += 1
        rows.append([object_type, object_id, item.get("source_file", ""), item.get("source_svg_id", ""), label, category, reason])

    for item in tags:
        if item.get("subsystem") == "Unknown":
            label = item.get("text", "")
            reason = item.get("unresolved_reason") or "Tag text matched a generic tag/equipment pattern but not QM/Jumper/QVB/QINFRA subsystem patterns."
            add("tag", item.get("tag_id", ""), item, label, reason, "no_matching_pattern_in_tag_layer_register")
    for item in boundaries:
        if item.get("subsystem") == "Unknown":
            label = item.get("label", "")
            if label:
                add("boundary", item.get("boundary_id", ""), item, label, item.get("unresolved_reason") or "Boundary label lacks a resolved subsystem token.", "no_matching_pattern_in_tag_layer_register")
            elif resolved_boundaries:
                add("boundary", item.get("boundary_id", ""), item, label, item.get("unresolved_reason") or "Boundary geometry is outside resolved subsystem boundaries.", "outside_all_resolved_boundaries")
            else:
                add("boundary", item.get("boundary_id", ""), item, label, item.get("unresolved_reason") or "Boundary has no label and no resolved subsystem boundary context exists.", "no_tag_or_label")
    for item in lines:
        if item.get("subsystem") == "Unknown":
            category = "outside_all_resolved_boundaries" if resolved_boundaries else "no_tag_or_label"
            reason = "Line has no direct label; no resolved subsystem boundary contains it." if resolved_boundaries else "Line has no direct tag/label and no resolved subsystem boundary context exists."
            add("line", item.get("line_id", ""), item, "", item.get("unresolved_reason") or reason, category)
    for item in arrows:
        if item.get("associated_subsystem") == "Unknown":
            category = "outside_all_resolved_boundaries" if resolved_boundaries else "no_tag_or_label"
            reason = "Arrow has no direct label; associated line is outside resolved subsystem boundaries." if resolved_boundaries else "Arrow has no direct tag/label and its associated line has no resolved subsystem."
            add("arrow", item.get("arrow_id", ""), item, "", item.get("unresolved_reason") or reason, category)
    return {"counts": counts, "rows": rows, "resolved_boundary_count": len(resolved_boundaries)}


def arrow_coverage_diagnostics(lines: list[dict[str, Any]], arrows: list[dict[str, Any]]) -> dict[str, Any]:
    arrow_line_ids = {arrow.get("associated_line_id") for arrow in arrows if arrow.get("associated_line_id")}
    rows = []
    for line in lines:
        if line.get("line_id") not in arrow_line_ids:
            rows.append([line.get("line_id", ""), line.get("source_file", ""), line.get("source_svg_id", ""), line.get("colour_bin", ""), "No marker-start/marker-end or draw.io endArrow/startArrow evidence on this line."])
    return {"line_count": len(lines), "arrow_count": len(arrows), "lines_without_arrow_evidence": len(rows), "rows": rows}



def qm_precision_diagnostics(lines: list[dict[str, Any]], arrows: list[dict[str, Any]], tags: list[dict[str, Any]], boundaries: list[dict[str, Any]]) -> dict[str, Any]:
    rows: list[list[Any]] = []
    rule_counts: Counter = Counter()

    def label_for(item: dict[str, Any]) -> str:
        if item.get("text"):
            return item["text"]
        if item.get("label"):
            return item["label"]
        labels = item.get("source_endpoint_labels") or {}
        if labels:
            return f"source={labels.get('source', '')}; target={labels.get('target', '')}"
        return ""

    for object_type, items in (("tag", tags), ("boundary", boundaries), ("line", lines), ("arrow", arrows)):
        for item in items:
            subsystem = item.get("subsystem") or item.get("associated_subsystem")
            if subsystem != "QM":
                continue
            rule = item.get("subsystem_rule") or "QM assignment without stored rule"
            label = label_for(item)
            rule_counts[rule] += 1
            rows.append([
                object_type,
                item.get("tag_id") or item.get("boundary_id") or item.get("line_id") or item.get("arrow_id") or "",
                item.get("source_file", ""),
                item.get("source_svg_id", ""),
                label,
                rule,
                "direct label or explicit draw.io endpoint label" if label else "NO_LABEL_REVIEW",
            ])
    flagged = [[rule, count] for rule, count in sorted(rule_counts.items()) if count > 10]
    return {"rows": rows, "rule_counts": [[rule, count] for rule, count in sorted(rule_counts.items())], "flagged_rules": flagged}


def build_layers(colour_counts: Counter, tag_counts: Counter, line_count: int, arrow_count: int, boundary_count: int, unresolved_count: int, subsystem_counts: Counter) -> list[dict[str, Any]]:
    rows = [
        ("process_lines", "process lines", line_count),
        ("blue_A", "BLUE → A / A′", colour_counts.get("blue_A", 0)),
        ("cyan_B_2K", "CYAN → B / B′", colour_counts.get("cyan_B_2K", 0)),
        ("green_W_coupler", "GREEN → W", colour_counts.get("green_W_coupler", 0)),
        ("grey_V_vent", "GREY → V", colour_counts.get("grey_V_vent", 0)),
        ("olive_S_line", "OLIVE → S", colour_counts.get("olive_S_line", 0)),
        ("red_orange_D_E", "RED / ORANGE → D/E", colour_counts.get("red_orange_D_E", 0)),
        ("unknown_black_or_other", "BLACK/unknown → structure/unknown", colour_counts.get("unknown_black_or_other", 0)),
        ("instruments", "instruments", tag_counts.get("instrument", 0)),
        ("valves", "valves", tag_counts.get("valve", 0)),
        ("equipment", "equipment", tag_counts.get("equipment", 0)),
        ("boundaries", "boundaries", boundary_count),
        ("arrows", "arrows", arrow_count),
        ("unresolved_objects", "unresolved objects", unresolved_count),
    ]
    rows.extend(("subsystem_" + subsystem.lower(), subsystem, subsystem_counts.get(subsystem, 0)) for subsystem in SUBSYSTEMS[:-1])
    return [{"layer_id": layer_id, "label": label, "item_count": count} for layer_id, label, count in rows]


def write_reports(run: dict[str, Any], assets: dict[str, list[dict[str, Any]]], counts: dict[str, Any], layers: list[dict[str, Any]]) -> None:
    inputs = [[item["path"], item["kind"], item["size_bytes"]] for item in run["inputs_found"]]
    colour_rows = [[colour_bin, counts["colour_counts"].get(colour_bin, 0)] for colour_bin in BIN_FILES]
    arrow_rows = [[colour_bin, counts["arrow_counts"].get(colour_bin, 0)] for colour_bin in BIN_FILES]
    resolved_subsystems = sum(v for k, v in counts["subsystem_counts"].items() if k != "Unknown")
    unknown_subsystems = counts["subsystem_counts"].get("Unknown", 0)
    common = f"""## Actual source files found
{markdown_table(inputs, ['path','kind','size_bytes'])}

## Source file counts
- SVG files found: {len(assets['svg'])}
- PDF files found: {len(assets['pdf'])}
- PPT/PPTX files found: {len(assets['ppt'])}

## SVG load status
{markdown_table([[x['path'], x['status'], x.get('error') or ''] for x in run['svg_load_status']], ['path','status','error'])}

## Colour bins detected
{markdown_table(colour_rows, ['colour_bin','process_line_count'])}

## Object counts
- Process lines: {counts['line_count']}
- Tags: {counts['tag_count']}
- Valves: {counts['tag_counts'].get('valve', 0)}
- Instruments: {counts['tag_counts'].get('instrument', 0)}
- Equipment: {counts['tag_counts'].get('equipment', 0)}
- Arrows: {counts['arrow_count']}
- Boundaries: {counts['boundary_count']}

## Arrow counts per colour
{markdown_table(arrow_rows, ['colour_bin','arrow_count'])}

## Subsystem counts
{markdown_table([[s, counts['subsystem_counts'].get(s, 0)] for s in SUBSYSTEMS], ['subsystem','object_count'])}

## Unresolved counts
- Unresolved arrows: {counts['unresolved_arrows']}
- Unresolved colours: {counts['unresolved_colours']}
- Unresolved tags: {counts['unresolved_tags']}
- Unresolved boundaries: {counts['unresolved_boundaries']}
- Unresolved objects: {counts['unresolved_objects']}

## Completion status
- {run['completion_status']}

## Known Limitations / Resolution Rates
- Arrow extraction: {counts['arrow_count']} arrow(s) resolved from {counts['line_count']} line(s). Direction is emitted only for explicit SVG marker or draw.io `endArrow`/`startArrow` evidence; connector lines without arrowhead evidence are not silently treated as flow direction.
- Arrow coverage: {counts['arrow_diagnostics']['lines_without_arrow_evidence']} line(s) lack explicit arrow evidence. The one resolved arrow comes from draw.io `endArrow` metadata in `QCELL_PARASITIC.drawio.svg`; the other local SVGs use plain SVG lines or non-arrow diagnostic graphics.
- Subsystem resolution: {resolved_subsystems} resolved vs {unknown_subsystems} Unknown. Unknown labels generally do not contain QM, Jumper, QVB, or QINFRA text evidence.
- Target for the next rule-improvement PR: reduce Unknown subsystem classification to ≤{counts['target_unknown_rate_percent']}% on this same local asset set without weakening evidence requirements.
- Colour-bin reconciliation: blue_A={counts['colour_counts'].get('blue_A', 0)}, cyan_B_2K={counts['colour_counts'].get('cyan_B_2K', 0)}, green_W_coupler={counts['colour_counts'].get('green_W_coupler', 0)}, grey_V_vent={counts['colour_counts'].get('grey_V_vent', 0)}, olive_S_line={counts['colour_counts'].get('olive_S_line', 0)}, red_orange_D_E={counts['colour_counts'].get('red_orange_D_E', 0)}, unknown_black_or_other={counts['colour_counts'].get('unknown_black_or_other', 0)}. Empty per-bin JSON files are retained as stable viewer/model outputs for toggle compatibility.
- Unresolved boundaries: {counts['unresolved_boundaries']}. These are reported separately; subsystem Unknown is driven by missing subsystem text evidence, not by boundary resolution alone.

## QM Precision Check
{markdown_table(counts['qm_diagnostics']['rows'] or [['none', '', '', '', '', '', '']], ['object_type','object_id','source_file','source_svg_id','label_text_used','subsystem_pattern','evidence_type'])}

## QM Pattern Review Flags (>10 matches)
{markdown_table(counts['qm_diagnostics']['flagged_rules'] or [['none', 0]], ['subsystem_pattern','match_count'])}

## Unknown Classification Breakdown
{markdown_table([[key, value] for key, value in counts['unknown_diagnostics']['counts'].items()], ['primary_failure_cause','unknown_object_count'])}

## Unknown Object Details
{markdown_table(counts['unknown_diagnostics']['rows'] or [['none', '', '', '', '', '', '']], ['object_type','object_id','source_file','source_svg_id','label','primary_failure_cause','reason'])}

## Arrow Coverage Details
{markdown_table(counts['arrow_diagnostics']['rows'] or [['none', '', '', '', '']], ['line_id','source_file','source_svg_id','colour_bin','reason'])}

## Unresolved tags / labels
{markdown_table(counts['unresolved_tag_rows'] or [['none', '', '', '']], ['tag_id','source_file','text','reason'])}

## Unresolved boundaries
{markdown_table(counts['unresolved_boundary_rows'] or [['none', '', '', '']], ['boundary_id','source_file','subsystem','reason'])}
"""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    (REPORTS_DIR / "W002_colour_line_validation.md").write_text("# W002 Colour Line Validation\n\n" + common, encoding="utf-8")
    (REPORTS_DIR / "W003_semantic_layer_validation.md").write_text("# W003 Semantic Layer Validation\n\n" + common + "\n## Semantic layers\n" + markdown_table([[x["layer_id"], x["label"], x["item_count"]] for x in layers], ["layer_id", "label", "count"]) + "\n", encoding="utf-8")
    (REPORTS_DIR / "W003_arrow_direction_validation.md").write_text("# W003 Arrow Direction Validation\n\n" + common, encoding="utf-8")

def write_viewer() -> None:
    html = """<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\"><title>ABACUS P&amp;ID Semantic Viewer</title></head><body><h1>ABACUS P&amp;ID Semantic Viewer</h1><p>Run the local asset pipeline to refresh semantic models, then serve this directory to inspect overlays.</p></body></html>"""
    VIEWER_DIR.mkdir(parents=True, exist_ok=True)
    PUBLISH_DIR.mkdir(parents=True, exist_ok=True)
    (VIEWER_DIR / "index.html").write_text(html, encoding="utf-8")
    (PUBLISH_DIR / "colour_line_collage.html").write_text(html.replace("P&amp;ID Semantic Viewer", "Colour Line Collage"), encoding="utf-8")


def build() -> dict[str, Any]:
    assets = discover_local_assets()
    ensure_local_svg_assets(assets)

    svg_results = [parse_svg(ROOT / item["path"], index) for index, item in enumerate(assets["svg"], 1)]
    lines = [line for result in svg_results for line in result["lines"]]
    arrows = [arrow for result in svg_results for arrow in result["arrows"]]
    tags = [tag for result in svg_results for tag in result["tags"]]
    boundaries = [boundary for result in svg_results for boundary in result["boundaries"]]

    for line in lines:
        line["viewer_layer_ids"] = ["process_lines", line["colour_bin"], "subsystem_" + line["subsystem"].lower()]
    for arrow in arrows:
        arrow["colour_bin"] = bin_colour(arrow.get("source_colour"))[0]
        arrow["viewer_layer_ids"] = ["arrows", arrow["colour_bin"], "subsystem_" + arrow["associated_subsystem"].lower()]
    for tag in tags:
        tag["viewer_layer_ids"] = [tag["semantic_class"] + "s", "subsystem_" + tag["subsystem"].lower()]
    for boundary in boundaries:
        boundary["viewer_layer_ids"] = ["boundaries", "subsystem_" + boundary["subsystem"].lower()]

    colour_counts = Counter(line["colour_bin"] for line in lines)
    arrow_counts = Counter(arrow["colour_bin"] for arrow in arrows)
    tag_counts = Counter(tag["semantic_class"] for tag in tags)
    subsystem_counts = Counter([*(item["subsystem"] for item in lines + tags + boundaries), *(item["associated_subsystem"] for item in arrows)])
    for subsystem in SUBSYSTEMS:
        subsystem_counts.setdefault(subsystem, 0)
    unresolved_arrows = [item for item in arrows if item.get("unresolved_reason") or not item.get("associated_line_id") or not item.get("direction_vector")]
    unresolved_colours = [item for item in lines if item.get("unresolved_reason")]
    unresolved_tags = [item for item in tags if item.get("unresolved_reason")]
    unresolved_boundaries = [item for item in boundaries if item.get("unresolved_reason")]
    unresolved_objects = len(unresolved_arrows) + len(unresolved_colours) + len(unresolved_tags) + len(unresolved_boundaries)
    unknown_diagnostics = unknown_resolution_diagnostics(lines, arrows, tags, boundaries)
    arrow_diagnostics = arrow_coverage_diagnostics(lines, arrows)
    qm_diagnostics = qm_precision_diagnostics(lines, arrows, tags, boundaries)

    run = {
        "schema_version": "0.3",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "asset_discovery_mode": "local_only",
        "inputs_found": [*assets["svg"], *assets["pdf"], *assets["ppt"]],
        "svg_load_status": [{"path": result["path"], "status": result["status"], "error": result.get("error")} for result in svg_results],
        "completion_status": "complete_nonzero" if lines and tags else "incomplete_no_nonzero_semantic_counts",
    }
    counts = {
        "line_count": len(lines),
        "tag_count": len(tags),
        "arrow_count": len(arrows),
        "boundary_count": len(boundaries),
        "colour_counts": dict(colour_counts),
        "arrow_counts": dict(arrow_counts),
        "tag_counts": dict(tag_counts),
        "subsystem_counts": dict(subsystem_counts),
        "unresolved_arrows": len(unresolved_arrows),
        "unresolved_colours": len(unresolved_colours),
        "unresolved_tags": len(unresolved_tags),
        "unresolved_boundaries": len(unresolved_boundaries),
        "unresolved_objects": unresolved_objects,
        "unresolved_tag_rows": [[item["tag_id"], item["source_file"], item["text"], item.get("unresolved_reason") or ""] for item in unresolved_tags],
        "unresolved_boundary_rows": [[item["boundary_id"], item["source_file"], item.get("subsystem", ""), item.get("unresolved_reason") or ""] for item in unresolved_boundaries],
        "unknown_diagnostics": unknown_diagnostics,
        "arrow_diagnostics": arrow_diagnostics,
        "qm_diagnostics": qm_diagnostics,
        "target_unknown_rate_percent": 50,
    }
    layers = build_layers(colour_counts, tag_counts, len(lines), len(arrows), len(boundaries), unresolved_objects, subsystem_counts)

    write_json(MODEL_DIR / "line_model.json", {**run, "summary": {"line_count": len(lines), "colour_counts": dict(colour_counts)}, "lines": lines})
    write_json(MODEL_DIR / "arrow_direction_model.json", {**run, "summary": {"arrow_count": len(arrows), "arrow_colour_counts": dict(arrow_counts), "unresolved_arrow_count": len(unresolved_arrows)}, "arrows": arrows})
    write_json(MODEL_DIR / "semantic_layer_model.json", {**run, "layers": layers})
    write_json(MODEL_DIR / "subsystem_model.json", {**run, "subsystems": [{"subsystem": subsystem, "item_count": subsystem_counts.get(subsystem, 0)} for subsystem in SUBSYSTEMS]})
    write_json(MODEL_DIR / "tag_layer_register.json", {**run, "summary": {"tag_count": len(tags), "tag_counts": dict(tag_counts), "unresolved_tag_count": len(unresolved_tags)}, "tags": tags, "boundaries": boundaries})
    for colour_bin, filename in BIN_FILES.items():
        bin_lines = [line for line in lines if line["colour_bin"] == colour_bin]
        write_json(LINES_DIR / filename, {**run, "colour_bin": colour_bin, "line_count": len(bin_lines), "lines": bin_lines})
    write_reports(run, assets, counts, layers)
    write_viewer()
    return {"status": "OK", "discovered_local_assets": assets, "extraction_status": run["completion_status"], "validation_status": "passed_svg_count_nonzero", **counts}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build ABACUS P&ID semantic models from local repository assets only.")
    parser.add_argument("command", nargs="?", default="all", choices=["all", "extract"], help="Run local asset discovery and extraction.")
    parser.parse_args(argv)
    try:
        print(json.dumps(build(), indent=2, ensure_ascii=False))
    except MissingLocalAssets:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
