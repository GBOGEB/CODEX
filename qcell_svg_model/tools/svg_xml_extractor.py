"""SVG/XML semantic extractor for QCELL viewer handover artifacts.

This module intentionally treats SVG (including Inkscape SVG and Draw.io XML
stored in ``.drawio.svg`` files) as the primary source of truth. It does not
open PDFs, rasterize drawings, or run OCR. The extractor preserves XML text
nodes, object identifiers, Inkscape layer labels, color metadata, and group
hierarchy so downstream YAML/JSON/viewer stages can retain authoring semantics.
"""

from __future__ import annotations

import argparse
import json
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from html import unescape
from pathlib import Path
from typing import Any, Iterable

INKSCAPE_NS = "http://www.inkscape.org/namespaces/inkscape"
SVG_NS = "http://www.w3.org/2000/svg"
XML_NS = "http://www.w3.org/XML/1998/namespace"

COLOR_KEYS = (
    "fill",
    "stroke",
    "fillColor",
    "strokeColor",
    "fontColor",
    "stop-color",
    "flood-color",
    "lighting-color",
)
COLOR_RE = re.compile(
    r"#[0-9a-fA-F]{3,8}|rgba?\([^)]*\)|hsla?\([^)]*\)|\b(?:none|currentColor)\b"
)


@dataclass(frozen=True)
class ExtractionPolicy:
    """Document non-negotiable extraction constraints."""

    primary_source: str = "svg_xml"
    ocr: bool = False
    rasterize: bool = False
    parse_pdf_first: bool = False
    preserve_text_nodes: bool = True
    preserve_layer_labels: bool = True
    preserve_object_ids: bool = True
    preserve_color_metadata: bool = True
    preserve_group_hierarchy: bool = True


def _local_name(tag: str) -> str:
    if "}" in tag:
        return tag.rsplit("}", 1)[1]
    return tag


def _namespace_uri(tag: str) -> str | None:
    if tag.startswith("{") and "}" in tag:
        return tag[1:].split("}", 1)[0]
    return None


def _attr(attrs: dict[str, str], namespace: str, local: str) -> str | None:
    return attrs.get(f"{{{namespace}}}{local}")


def _plain_attrs(attrs: dict[str, str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for key, value in attrs.items():
        if key.startswith("{"):
            uri, local = key[1:].split("}", 1)
            if uri == INKSCAPE_NS:
                out[f"inkscape:{local}"] = value
            elif uri == XML_NS:
                out[f"xml:{local}"] = value
            elif uri == SVG_NS:
                out[local] = value
            else:
                out[f"{{{uri}}}{local}"] = value
        else:
            out[key] = value
    return out


def _parse_style(style: str | None) -> dict[str, str]:
    result: dict[str, str] = {}
    if not style:
        return result
    for part in style.split(";"):
        separator = ":" if ":" in part else "=" if "=" in part else None
        if separator is None:
            if part.strip():
                result[part.strip()] = "true"
            continue
        key, value = part.split(separator, 1)
        key = key.strip()
        value = value.strip()
        if key:
            result[key] = value
    return result


def _collect_text(element: ET.Element) -> str:
    parts: list[str] = []
    for text in element.itertext():
        clean = " ".join(unescape(text).split())
        if clean:
            parts.append(clean)
    return " ".join(parts)


def _collect_colors(attrs: dict[str, str], style: dict[str, str]) -> dict[str, str]:
    colors: dict[str, str] = {}
    plain = _plain_attrs(attrs)
    color_key_aliases = {
        "fillColor": "fill",
        "strokeColor": "stroke",
        "fontColor": "font",
    }
    for key in COLOR_KEYS:
        value = style.get(key) or plain.get(key)
        if value and (COLOR_RE.search(value) or value.startswith("url(")):
            colors[color_key_aliases.get(key, key)] = value
    return colors


def _root_namespaces(path: Path) -> dict[str, str]:
    namespaces: dict[str, str] = {}
    for event, item in ET.iterparse(path, events=("start-ns",)):
        prefix, uri = item
        namespaces[prefix or "default"] = uri
    return namespaces


def _child_elements(element: ET.Element) -> Iterable[ET.Element]:
    return (child for child in list(element) if isinstance(child.tag, str))


def _extract_svg(root: ET.Element, namespaces: dict[str, str]) -> dict[str, Any]:
    layers: list[dict[str, Any]] = []
    objects: list[dict[str, Any]] = []
    hierarchy: list[dict[str, str]] = []

    def walk(
        element: ET.Element,
        parent_xml_id: str | None,
        layer_stack: list[dict[str, str]],
    ) -> None:
        attrs = element.attrib
        tag = _local_name(element.tag)
        xml_id = attrs.get("id") or _attr(attrs, XML_NS, "id")
        label = _attr(attrs, INKSCAPE_NS, "label")
        groupmode = _attr(attrs, INKSCAPE_NS, "groupmode")
        object_id = xml_id or f"anonymous:{len(objects) + 1}"

        current_stack = layer_stack
        if tag == "g" and groupmode == "layer":
            layer = {
                "id": object_id,
                "label": label or object_id,
                "parent_id": parent_xml_id,
                "depth": len(layer_stack),
                "path": [*[item["label"] for item in layer_stack], label or object_id],
                "attributes": _plain_attrs(attrs),
            }
            layers.append(layer)
            current_stack = [*layer_stack, {"id": object_id, "label": layer["label"]}]

        if parent_xml_id and xml_id:
            hierarchy.append({"parent_id": parent_xml_id, "child_id": xml_id})

        style = _parse_style(attrs.get("style"))
        text = (
            _collect_text(element) if tag in {"text", "tspan", "title", "desc"} else ""
        )
        object_record = {
            "id": object_id,
            "xml_id": xml_id,
            "tag": tag,
            "namespace": _namespace_uri(element.tag),
            "parent_id": parent_xml_id,
            "inkscape_label": label,
            "inkscape_groupmode": groupmode,
            "layer_path": [item["label"] for item in current_stack],
            "attributes": _plain_attrs(attrs),
            "style": style,
            "colors": _collect_colors(attrs, style),
            "text": text,
            "children": [
                child.attrib.get("id")
                for child in _child_elements(element)
                if child.attrib.get("id")
            ],
        }
        objects.append(object_record)

        next_parent = xml_id or parent_xml_id
        for child in _child_elements(element):
            walk(child, next_parent, current_stack)

    walk(root, None, [])
    return {
        "source_kind": (
            "inkscape_svg"
            if any(
                layer.get("attributes", {}).get("inkscape:groupmode") == "layer"
                for layer in layers
            )
            else "svg_xml"
        ),
        "namespaces": namespaces,
        "layers": layers,
        "objects": objects,
        "group_hierarchy": hierarchy,
    }


def _extract_drawio(root: ET.Element, namespaces: dict[str, str]) -> dict[str, Any]:
    diagrams: list[dict[str, Any]] = []
    objects: list[dict[str, Any]] = []
    hierarchy: list[dict[str, str]] = []
    layers: list[dict[str, Any]] = []

    for diagram in root.findall("diagram"):
        diagram_id = diagram.attrib.get("id") or f"diagram:{len(diagrams) + 1}"
        diagram_name = diagram.attrib.get("name", diagram_id)
        diagram_record = {
            "id": diagram_id,
            "label": diagram_name,
            "name": diagram_name,
            "attributes": _plain_attrs(diagram.attrib),
        }
        diagrams.append(diagram_record)
        layers.append(
            {
                "id": diagram_id,
                "label": diagram_name,
                "parent_id": None,
                "depth": 0,
                "path": [diagram_name],
                "attributes": _plain_attrs(diagram.attrib),
            }
        )

        cells = diagram.findall(".//mxCell")
        cell_labels: dict[str, str] = {}
        for cell in cells:
            cell_id = cell.attrib.get("id")
            value = unescape(cell.attrib.get("value", ""))
            if cell_id:
                cell_labels[cell_id] = value or cell_id

        for cell in cells:
            cell_id = (
                cell.attrib.get("id") or f"{diagram_id}:anonymous:{len(objects) + 1}"
            )
            parent_id = cell.attrib.get("parent")
            if parent_id:
                hierarchy.append(
                    {
                        "parent_id": parent_id,
                        "child_id": cell_id,
                        "diagram_id": diagram_id,
                    }
                )
            style = _parse_style(cell.attrib.get("style"))
            geom = cell.find("mxGeometry")
            is_group = (
                style.get("swimlane") is not None
                or style.get("shape") == "swimlane"
                or cell.attrib.get("vertex") == "1"
                and any(other.attrib.get("parent") == cell_id for other in cells)
            )
            value = unescape(cell.attrib.get("value", ""))
            parent_label = cell_labels.get(parent_id or "")
            layer_path = [diagram_name] + (
                [parent_label] if parent_label and parent_id not in {"0", "1"} else []
            )
            record = {
                "id": cell_id,
                "xml_id": cell_id,
                "tag": "mxCell",
                "diagram_id": diagram_id,
                "diagram_name": diagram_name,
                "parent_id": parent_id,
                "value": value,
                "text": value,
                "is_group": is_group,
                "layer_path": layer_path,
                "source": cell.attrib.get("source"),
                "target": cell.attrib.get("target"),
                "attributes": _plain_attrs(cell.attrib),
                "style": style,
                "colors": _collect_colors(cell.attrib, style),
                "geometry": _plain_attrs(geom.attrib) if geom is not None else {},
            }
            objects.append(record)
            if is_group and value:
                layers.append(
                    {
                        "id": cell_id,
                        "label": value,
                        "parent_id": diagram_id,
                        "depth": 1,
                        "path": [diagram_name, value],
                        "attributes": _plain_attrs(cell.attrib),
                        "colors": record["colors"],
                    }
                )

    return {
        "source_kind": "drawio_mxfile_svg_xml",
        "namespaces": namespaces,
        "diagrams": diagrams,
        "layers": layers,
        "objects": objects,
        "group_hierarchy": hierarchy,
    }


def extract_svg_xml(path: str | Path) -> dict[str, Any]:
    """Extract semantic SVG/XML metadata without OCR, rasterization, or PDF parsing."""

    source = Path(path)
    namespaces = _root_namespaces(source)
    root = ET.parse(source).getroot()
    policy = ExtractionPolicy().__dict__
    if _local_name(root.tag) == "mxfile":
        payload = _extract_drawio(root, namespaces)
    else:
        payload = _extract_svg(root, namespaces)
    payload.update(
        {
            "source_path": str(source),
            "root_tag": _local_name(root.tag),
            "extraction_policy": policy,
        }
    )
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Extract SVG XML semantics without OCR/raster/PDF preprocessing"
    )
    parser.add_argument(
        "source", type=Path, help="Source SVG or .drawio.svg XML artifact"
    )
    parser.add_argument(
        "--output", "-o", type=Path, help="Write JSON manifest to this path"
    )
    args = parser.parse_args(argv)

    manifest = extract_svg_xml(args.source)
    encoded = json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded + "\n", encoding="utf-8")
    else:
        print(encoded)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
