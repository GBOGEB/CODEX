from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "mission_control" / "mycelium" / "interaction_graph.json"
OUT = ROOT / "mission_control" / "mycelium" / "graph_analysis.json"
PAGES_OUT = ROOT / "docs" / "data" / "missioncontrol_graph_analysis.json"
SVG_OUT = ROOT / "docs" / "assets" / "missioncontrol" / "missioncontrol_degree_distribution.svg"


def build_analysis(graph: dict[str, Any]) -> dict[str, Any]:
    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])
    degree = {
        node["id"]: {
            "id": node["id"],
            "label": node.get("label"),
            "type": node.get("type"),
            "state": node.get("state"),
            "in_degree": 0,
            "out_degree": 0,
            "total_degree": 0,
        }
        for node in nodes
    }
    for edge in edges:
        if edge.get("from") in degree:
            degree[edge["from"]]["out_degree"] += 1
        if edge.get("to") in degree:
            degree[edge["to"]]["in_degree"] += 1
    for row in degree.values():
        row["total_degree"] = row["in_degree"] + row["out_degree"]
    ranked = sorted(degree.values(), key=lambda row: (-row["total_degree"], row["id"]))
    distribution = Counter(row["total_degree"] for row in ranked)
    n = len(nodes)
    return {
        "schema_version": "0.1",
        "source_graph": "mission_control/mycelium/interaction_graph.json",
        "pages_source_graph": "docs/data/missioncontrol_interaction_graph.json",
        "authority_class": "DERIVED_PROJECTION_ONLY",
        "authority_transfer": False,
        "graph": {
            "node_count": n,
            "edge_count": len(edges),
            "density": round(len(edges) / (n * (n - 1)), 6) if n > 1 else 0.0,
            "directed": True,
        },
        "node_type_counts": dict(sorted(Counter(str(x.get("type", "UNSPECIFIED")) for x in nodes).items())),
        "node_state_counts": dict(sorted(Counter(str(x.get("state", "UNSPECIFIED")) for x in nodes).items())),
        "degree_distribution": [
            {"degree": degree_value, "count": distribution[degree_value]}
            for degree_value in sorted(distribution)
        ],
        "top_degree_nodes": ranked[:20],
        "renderer_contract": {
            "core": "HTML_SVG",
            "plotly": "OPTIONAL_INTERACTIVE_PROJECTION",
            "matplotlib": "OPTIONAL_STATIC_PROJECTION",
            "plotly_failure_blocks_core": False,
            "matplotlib_failure_blocks_core": False,
        },
    }


def build_svg(analysis: dict[str, Any]) -> str:
    data = analysis["degree_distribution"]
    width, height = 960, 420
    left, right, top, bottom = 72, 24, 40, 68
    plot_w = width - left - right
    plot_h = height - top - bottom
    maximum = max((row["count"] for row in data), default=1)
    bar_w = plot_w / max(len(data), 1) * 0.68
    bars: list[str] = []
    labels: list[str] = []
    for i, row in enumerate(data):
        cx = left + (i + 0.5) * plot_w / max(len(data), 1)
        bar_h = row["count"] / maximum * plot_h
        y = top + plot_h - bar_h
        bars.append(
            f'<rect x="{cx-bar_w/2:.1f}" y="{y:.1f}" width="{bar_w:.1f}" '
            f'height="{bar_h:.1f}" rx="3"><title>degree {row["degree"]}: '
            f'{row["count"]} nodes</title></rect>'
        )
        labels.append(
            f'<text x="{cx:.1f}" y="{height-38}" text-anchor="middle">{row["degree"]}</text>'
            f'<text x="{cx:.1f}" y="{max(top+14, y-6):.1f}" text-anchor="middle">{row["count"]}</text>'
        )
    graph = analysis["graph"]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
<title id="title">MissionControl graph degree distribution</title>
<desc id="desc">Derived from the canonical interaction graph. {graph["node_count"]} nodes, {graph["edge_count"]} edges, directed density {graph["density"]}.</desc>
<style>text{{font:14px system-ui,sans-serif;fill:#334155}}rect{{fill:#64748b}}line{{stroke:#94a3b8;stroke-width:1}}.title{{font-size:20px;font-weight:700;fill:#0f172a}}.sub{{font-size:13px;fill:#64748b}}</style>
<rect width="100%" height="100%" fill="#fff"/>
<text class="title" x="{left}" y="24">Degree distribution</text>
<text class="sub" x="{left}" y="42">{graph["node_count"]} nodes · {graph["edge_count"]} edges · density {graph["density"]}</text>
<line x1="{left}" y1="{top+plot_h}" x2="{width-right}" y2="{top+plot_h}"/><line x1="{left}" y1="{top}" x2="{left}" y2="{top+plot_h}"/>
{''.join(bars)}{''.join(labels)}
<text x="{width/2}" y="{height-8}" text-anchor="middle">Total degree (in + out)</text>
<text transform="translate(18 {height/2}) rotate(-90)" text-anchor="middle">Node count</text>
</svg>
'''


def main() -> None:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    analysis = build_analysis(graph)
    payload = json.dumps(analysis, indent=2) + "\n"
    OUT.write_text(payload, encoding="utf-8")
    PAGES_OUT.parent.mkdir(parents=True, exist_ok=True)
    PAGES_OUT.write_text(payload, encoding="utf-8")
    SVG_OUT.parent.mkdir(parents=True, exist_ok=True)
    SVG_OUT.write_text(build_svg(analysis), encoding="utf-8")
    print(
        "MissionControl graph publication: "
        f'{analysis["graph"]["node_count"]} nodes / '
        f'{analysis["graph"]["edge_count"]} edges / '
        f'density {analysis["graph"]["density"]}'
    )


if __name__ == "__main__":
    main()
