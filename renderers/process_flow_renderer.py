"""process_flow_renderer.py – Converts a *process_flow* YAML/dict schema to SVG.

Wave: W003
Subwave: W003.2

Schema expected
---------------
type: process_flow
title: <string>
nodes:
  - id: <str>
    label: <str>
edges:
  - from: <str>
    to: <str>
"""
from __future__ import annotations

from typing import Any

from renderers.svg_renderer import SVGRenderer, LINEAGE as _BASE_LINEAGE


# Lineage metadata required by governance
LINEAGE: dict[str, Any] = {
    **_BASE_LINEAGE,
    "renderer": "process_flow",
}

# Layout constants
_NODE_W = 140
_NODE_H = 44
_H_GAP = 60   # horizontal gap between node centres
_MARGIN_X = 80
_MARGIN_Y = 60
_SVG_HEIGHT = 200

# Arrow marker XML (injected into <defs>)
_ARROW_MARKER = (
    '<marker id="arrow" markerWidth="10" markerHeight="7" '
    'refX="10" refY="3.5" orient="auto">'
    '<polygon points="0 0, 10 3.5, 0 7" fill="#555"/>'
    '</marker>'
)


def _validate_schema(schema: dict[str, Any]) -> None:
    """Raise ValueError for invalid process_flow schemas."""
    if not isinstance(schema, dict):
        raise ValueError("Schema must be a dict")
    schema_type = schema.get("type")
    if schema_type != "process_flow":
        raise ValueError(
            f"Expected schema type 'process_flow', got {schema_type!r}"
        )
    if "nodes" not in schema:
        raise ValueError("Schema missing required key 'nodes'")
    if not isinstance(schema["nodes"], list):
        raise ValueError("'nodes' must be a list")
    for node in schema["nodes"]:
        if "id" not in node or "label" not in node:
            raise ValueError(
                f"Each node must have 'id' and 'label'; got {node!r}"
            )
    edges = schema.get("edges", [])
    if not isinstance(edges, list):
        raise ValueError("'edges' must be a list")
    node_ids = {n["id"] for n in schema["nodes"]}
    for edge in edges:
        if "from" not in edge or "to" not in edge:
            raise ValueError(
                f"Each edge must have 'from' and 'to'; got {edge!r}"
            )
        if edge["from"] not in node_ids:
            raise ValueError(
                f"Edge references unknown node id {edge['from']!r}"
            )
        if edge["to"] not in node_ids:
            raise ValueError(
                f"Edge references unknown node id {edge['to']!r}"
            )


def render_process_flow(
    schema: dict[str, Any],
    *,
    scale: float = 1.0,
) -> str:
    """Convert a *process_flow* schema dict to an SVG string.

    Parameters
    ----------
    schema:
        Validated process_flow dict (as parsed from YAML).
    scale:
        Uniform scale factor applied to width/height/spacing.

    Returns
    -------
    str
        Well-formed SVG markup.
    """
    _validate_schema(schema)

    nodes: list[dict[str, str]] = schema.get("nodes", [])
    edges: list[dict[str, str]] = schema.get("edges", [])
    title: str = schema.get("title", "")

    if not nodes:
        # Return a minimal valid SVG for empty graphs
        svg = SVGRenderer(
            width=max(1, int(200 * scale)),
            height=max(1, int(100 * scale)),
            renderer_name=LINEAGE["renderer"],
        )
        svg.add_text(
            int(100 * scale),
            int(50 * scale),
            "(empty graph)",
            fill="#888",
        )
        return svg.render()

    n = len(nodes)
    node_w = int(_NODE_W * scale)
    node_h = int(_NODE_H * scale)
    h_gap = int(_H_GAP * scale)
    margin_x = int(_MARGIN_X * scale)
    margin_y = int(_MARGIN_Y * scale)
    title_offset = int(30 * scale) if title else 0

    total_width = margin_x * 2 + n * node_w + (n - 1) * h_gap
    total_height = int(_SVG_HEIGHT * scale) + title_offset

    svg = SVGRenderer(width=total_width, height=total_height, renderer_name=LINEAGE["renderer"])
    svg.add_defs(_ARROW_MARKER)

    # Title
    if title:
        svg.add_text(
            total_width // 2,
            int(20 * scale),
            title,
            font_size=max(10, int(15 * scale)),
            fill="#1a1a2e",
        )

    # Compute node centre positions
    centres: dict[str, tuple[float, float]] = {}
    for i, node in enumerate(nodes):
        cx = margin_x + i * (node_w + h_gap) + node_w / 2
        cy = margin_y + title_offset + node_h / 2
        centres[node["id"]] = (cx, cy)

    # Draw edges first (so they appear behind nodes)
    for edge in edges:
        src_cx, src_cy = centres[edge["from"]]
        dst_cx, dst_cy = centres[edge["to"]]

        # Shorten line so it starts/ends at node border, not centre
        src_x = src_cx + node_w / 2
        dst_x = dst_cx - node_w / 2
        svg.add_line(src_x, src_cy, dst_x, dst_cy)

    # Draw nodes
    for node in nodes:
        cx, cy = centres[node["id"]]
        x = cx - node_w / 2
        y = cy - node_h / 2
        svg.add_rect(x, y, node_w, node_h)
        svg.add_text(cx, cy, node["label"], font_size=max(9, int(13 * scale)))

    return svg.render()


def lineage_metadata() -> dict[str, Any]:
    """Return a copy of the lineage metadata block for this renderer."""
    return dict(LINEAGE)
