"""Build the QPS semantic navigation graph from the node YAML records (no hand-drawn SVG).

Sources:
  docs/qps-slide-system/yaml/nodes/*.yaml     one record per node (schema: yaml/schema.node.yaml)
  docs/qps-slide-system/styles/tokens.yaml    colors and typography
Outputs:
  docs/qps-slide-system/svg/navigation/qps-graph-mvp.svg   tree edges (parent) solid, interface links dashed
  docs/qps-slide-system/html/graph/index.html              graph page + node table fallback
  docs/qps-slide-system/html/node/<stem>.html              one detail page per node record

Tree vs links: `parent` gives the SBS tree; `interfaces` are links between nodes,
drawn once per unordered pair. An interface that coincides with a tree edge is
listed on the node pages but not drawn twice.

Deterministic; a test fails if the committed outputs are stale. Regenerate with:
  python tools/build_qps_node_graph.py           (write)
  python tools/build_qps_node_graph.py --check   (exit 1 when stale)
"""
from __future__ import annotations

import argparse
import sys
from html import escape
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
SYSTEM = REPO_ROOT / "docs" / "qps-slide-system"
NODES_DIR = SYSTEM / "yaml" / "nodes"
SCHEMA = SYSTEM / "yaml" / "schema.node.yaml"
TOKENS = SYSTEM / "styles" / "tokens.yaml"
SVG_PATH = "svg/navigation/qps-graph-mvp.svg"
GRAPH_PATH = "html/graph/index.html"
NODE_PATH = "html/node/{stem}.html"
ROOT = "ROOT"

BOX_W, BOX_H = 180, 48
COL_X0, COL_DX = 40, 240
ROW_Y0, ROW_DY = 40, 64
LANE_GAP, LANE_DX = 40, 16
NAV_LINKS = (
    ("Back to graph", "../graph/index.html"),
    ("Controls matrix", "../../decks/control_system.yaml"),
    ("Utilities/plots source", "../../decks/style_system.yaml"),
    ("Deck navigator", "../../index.html"),
)


class NodeGraphError(ValueError):
    """A node record breaks the schema or the graph rules."""


def load_nodes(nodes_dir: Path = NODES_DIR, schema_path: Path = SCHEMA) -> dict[str, dict[str, Any]]:
    """Load and validate every node record; keyed by node id, each carrying its file stem."""
    schema = yaml.safe_load(schema_path.read_text(encoding="utf-8"))["node"]
    required = [k for k in schema if k != "links"]
    nodes: dict[str, dict[str, Any]] = {}
    for path in sorted(nodes_dir.glob("*.yaml")):
        record = (yaml.safe_load(path.read_text(encoding="utf-8")) or {}).get("node")
        if not isinstance(record, dict):
            raise NodeGraphError(f"{path.name}: missing top-level 'node' mapping")
        missing = [k for k in required if k not in record]
        if missing:
            raise NodeGraphError(f"{path.name}: missing keys {missing}")
        for key in required:
            if isinstance(schema[key], list) and not isinstance(record[key], list):
                raise NodeGraphError(f"{path.name}: '{key}' must be a list")
        node_id = str(record["id"])
        if node_id in nodes:
            raise NodeGraphError(f"{path.name}: duplicate node id {node_id} (also in {nodes[node_id]['stem']}.yaml)")
        nodes[node_id] = {**record, "id": node_id, "stem": path.stem, "links": record.get("links") or {}}
    if not nodes:
        raise NodeGraphError(f"no node records in {nodes_dir}")
    for node in nodes.values():
        if node["parent"] != ROOT and node["parent"] not in nodes:
            raise NodeGraphError(f"{node['id']}: parent {node['parent']} is not a node")
        for other in node["interfaces"]:
            if other not in nodes:
                raise NodeGraphError(f"{node['id']}: interface {other} is not a node")
            if other == node["id"]:
                raise NodeGraphError(f"{node['id']}: interface to itself")
    for node in nodes.values():
        seen, cur = set(), node["id"]
        while cur != ROOT:
            if cur in seen:
                raise NodeGraphError(f"{node['id']}: parent chain has a cycle")
            seen.add(cur)
            cur = nodes[cur]["parent"]
    return nodes


def children(nodes: dict[str, dict[str, Any]], parent: str) -> list[str]:
    return sorted(n for n, rec in nodes.items() if rec["parent"] == parent)


def tree_edges(nodes: dict[str, dict[str, Any]]) -> list[tuple[str, str]]:
    return sorted((rec["parent"], n) for n, rec in nodes.items() if rec["parent"] != ROOT)


def link_edges(nodes: dict[str, dict[str, Any]]) -> list[tuple[str, str]]:
    """Unordered interface pairs that are not already tree edges."""
    tree = {frozenset(e) for e in tree_edges(nodes)}
    pairs = {tuple(sorted((n, o))) for n, rec in nodes.items() for o in rec["interfaces"]}
    return sorted(p for p in pairs if frozenset(p) not in tree)


def layout(nodes: dict[str, dict[str, Any]]) -> dict[str, tuple[int, int]]:
    """Column = tree depth, one row per node in tree preorder, so no row holds two boxes."""
    order: list[tuple[str, int]] = []

    def walk(node_id: str, depth: int) -> None:
        order.append((node_id, depth))
        for kid in children(nodes, node_id):
            walk(kid, depth + 1)

    for top in children(nodes, ROOT):
        walk(top, 0)
    return {n: (COL_X0 + d * COL_DX, ROW_Y0 + row * ROW_DY) for row, (n, d) in enumerate(order)}


def _tokens() -> dict[str, Any]:
    return yaml.safe_load(TOKENS.read_text(encoding="utf-8"))


def render_svg(nodes: dict[str, dict[str, Any]]) -> str:
    colors, font = _tokens()["colors"], _tokens()["typography"]["font_stack"]
    pos = layout(nodes)
    lane_x0 = max(x for x, _ in pos.values()) + BOX_W + LANE_GAP
    width = lane_x0 + len(link_edges(nodes)) * LANE_DX + COL_X0
    height = max(y for _, y in pos.values()) + BOX_H + ROW_Y0 + 40
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="graph-title">',
        "  <title id=\"graph-title\">QPS semantic navigation graph (generated from yaml/nodes)</title>",
        "  <style>",
        f"    .node {{ fill: {colors['panel']}; stroke: {colors['accent']}; stroke-width: 2; }}",
        f"    .label {{ fill: {colors['text']}; font: 15px {font}; text-anchor: middle; }}",
        f"    .type {{ fill: {colors['text']}; opacity: 0.7; font: 11px {font}; text-anchor: middle; }}",
        "    .tree { fill: none; stroke: #6b7280; stroke-width: 1.5; }",
        f"    .link {{ fill: none; stroke: {colors['warning']}; stroke-width: 1.5; stroke-dasharray: 6 4; }}",
        f"    .legend {{ fill: {colors['text']}; font: 12px {font}; }}",
        "  </style>",
    ]
    for parent, child in tree_edges(nodes):
        (px, py), (cx, cy) = pos[parent], pos[child]
        x1, y1, x2, y2 = px + BOX_W, py + BOX_H // 2, cx, cy + BOX_H // 2
        mid = (x1 + x2) // 2
        out.append(f'  <path class="tree" data-edge="tree" data-from="{escape(parent)}" data-to="{escape(child)}" d="M{x1} {y1} H{mid} V{y2} H{x2}"/>')
    for lane, (a, b) in enumerate(link_edges(nodes)):
        # Each link gets its own vertical lane right of every box; the stubs run along
        # the endpoint rows, which hold no other box, so a link never hides a node.
        (ax, ay), (bx, by) = pos[a], pos[b]
        x = lane_x0 + lane * LANE_DX
        out.append(
            f'  <path class="link" data-edge="link" data-from="{escape(a)}" data-to="{escape(b)}" '
            f'd="M{ax + BOX_W} {ay + BOX_H // 2} H{x} V{by + BOX_H // 2} H{bx + BOX_W}"/>'
        )
    for node_id in sorted(nodes, key=lambda n: (pos[n][0], pos[n][1])):
        rec, (x, y) = nodes[node_id], pos[node_id]
        href = "../../" + NODE_PATH.format(stem=rec["stem"])
        cx = x + BOX_W // 2
        out.append(
            f'  <a href="{href}" data-node="{escape(node_id)}"><title>{escape(node_id)} ({escape(str(rec["type"]))})</title>'
            f'<rect class="node" x="{x}" y="{y}" width="{BOX_W}" height="{BOX_H}" rx="8"/>'
            f'<text class="label" x="{cx}" y="{y + 22}">{escape(node_id)}</text>'
            f'<text class="type" x="{cx}" y="{y + 39}">{escape(str(rec["type"]))}</text></a>'
        )
    ly = height - 20
    out.append(f'  <path class="tree" d="M{COL_X0} {ly} H{COL_X0 + 40}"/><text class="legend" x="{COL_X0 + 48}" y="{ly + 4}">tree (parent)</text>')
    out.append(f'  <path class="link" d="M{COL_X0 + 170} {ly} H{COL_X0 + 210}"/><text class="legend" x="{COL_X0 + 218}" y="{ly + 4}">interface link</text>')
    out.append("</svg>")
    return "\n".join(out) + "\n"


def _page(title: str, body: list[str]) -> str:
    colors, font = _tokens()["colors"], _tokens()["typography"]["font_stack"]
    head = [
        "<!doctype html>",
        '<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">',
        f"<title>{escape(title)}</title>",
        "<!-- generated by tools/build_qps_node_graph.py; do not edit by hand -->",
        "<style>",
        f"body{{background:{colors['bg']};color:{colors['text']};font-family:{font};max-width:1180px;margin:auto;padding:0 16px}}",
        f"a{{color:{colors['accent']}}}",
        "table{border-collapse:collapse;width:100%}",
        "th,td{border:1px solid #334155;padding:4px 8px;text-align:left;vertical-align:top}",
        "object{max-width:100%;height:auto}",
        "</style></head><body>",
    ]
    return "\n".join(head + body + ["</body></html>"]) + "\n"


def _node_link(nodes: dict[str, dict[str, Any]], node_id: str) -> str:
    return f'<a href="{nodes[node_id]["stem"]}.html">{escape(node_id)}</a>'


def render_graph_page(nodes: dict[str, dict[str, Any]]) -> str:
    rows = []
    for node_id in sorted(nodes):
        rec = nodes[node_id]
        parent = "—" if rec["parent"] == ROOT else escape(rec["parent"])
        ifaces = ", ".join(escape(i) for i in sorted(rec["interfaces"])) or "—"
        rows.append(
            f'<tr><td><a href="../node/{rec["stem"]}.html">{escape(node_id)}</a></td>'
            f"<td>{escape(str(rec['type']))}</td><td>{parent}</td><td>{ifaces}</td></tr>"
        )
    body = [
        "<h1>QPS Semantic Navigation Graph</h1>",
        (
            "<p>Generated from <code>yaml/nodes/*.yaml</code>. Solid edges are the SBS tree (<code>parent</code>); "
            "dashed edges are <code>interfaces</code>. Click a node to open its detail page.</p>"
        ),
        f'<object type="image/svg+xml" data="../../{SVG_PATH}">QPS graph (SVG)</object>',
        "<h2>Nodes</h2>",
        "<table><thead><tr><th>Node</th><th>Type</th><th>Parent</th><th>Interfaces</th></tr></thead><tbody>",
        *rows,
        "</tbody></table>",
    ]
    return _page("QPS Graph", body)


def render_node_page(nodes: dict[str, dict[str, Any]], node_id: str) -> str:
    rec = nodes[node_id]
    declared_by = sorted(n for n, r in nodes.items() if node_id in r["interfaces"] and n not in rec["interfaces"])
    kids = children(nodes, node_id)

    def items(values: list[Any]) -> str:
        return ", ".join(f"<code>{escape(str(v))}</code>" for v in values) or "—"

    rows = [
        ("Type", escape(str(rec["type"]))),
        ("Parent", "— (root)" if rec["parent"] == ROOT else _node_link(nodes, rec["parent"])),
        ("Children", ", ".join(_node_link(nodes, k) for k in kids) or "—"),
        ("Interfaces", ", ".join(_node_link(nodes, i) for i in sorted(rec["interfaces"])) or "—"),
        ("Interfaced by", ", ".join(_node_link(nodes, i) for i in declared_by) or "—"),
        ("Plots", items(rec["plots"])),
        ("Slides", items(rec["slides"])),
        ("Source refs", items(rec["source_refs"])),
    ]
    links = [(k, v) for k, v in sorted(rec["links"].items())]
    body = [
        f"<h1>Node: {escape(node_id)}</h1>",
        f'<p>YAML record: <a href="../../yaml/nodes/{rec["stem"]}.yaml"><code>yaml/nodes/{rec["stem"]}.yaml</code></a></p>',
        "<table><tbody>",
        *(f"<tr><th>{k}</th><td>{v}</td></tr>" for k, v in rows),
        "</tbody></table>",
        "<h2>Navigation</h2>",
        "<ul>",
        *(f'  <li><a href="{href}">{label}</a></li>' for label, href in NAV_LINKS),
        *(f'  <li><a href="{escape(str(v))}">{escape(str(k))}</a></li>' for k, v in links),
        "</ul>",
    ]
    return _page(f"{node_id} node", body)


def render_all(nodes: dict[str, dict[str, Any]] | None = None) -> dict[str, str]:
    """All outputs, keyed by path relative to docs/qps-slide-system."""
    nodes = load_nodes() if nodes is None else nodes
    outputs = {SVG_PATH: render_svg(nodes), GRAPH_PATH: render_graph_page(nodes)}
    for node_id, rec in nodes.items():
        outputs[NODE_PATH.format(stem=rec["stem"])] = render_node_page(nodes, node_id)
    return dict(sorted(outputs.items()))


def stale_outputs(outputs: dict[str, str]) -> list[str]:
    stale = []
    for rel, text in outputs.items():
        path = SYSTEM / rel
        if not path.exists() or path.read_text(encoding="utf-8") != text:
            stale.append(rel)
    known = {Path(rel).name for rel in outputs if rel.startswith("html/node/")}
    stale += [f"html/node/{p.name} (no node record)" for p in sorted((SYSTEM / "html" / "node").glob("*.html")) if p.name not in known]
    return stale


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="exit 1 if committed outputs are stale")
    args = parser.parse_args(argv)
    outputs = render_all()
    if args.check:
        stale = stale_outputs(outputs)
        for rel in stale:
            print(f"stale: {rel}", file=sys.stderr)
        return 1 if stale else 0
    for rel, text in outputs.items():
        path = SYSTEM / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")
    print(f"wrote {len(outputs)} files under {SYSTEM}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
