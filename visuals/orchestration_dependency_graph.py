"""Generate an orchestration dependency graph from agent_runtime/agent_topology.json.

Reads agent roles and root from the topology manifest and produces a
Plotly network graph HTML artifact.

Usage:
    python visuals/orchestration_dependency_graph.py [--topology PATH] [--output PATH]
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_TOPOLOGY = REPO_ROOT / "agent_runtime" / "agent_topology.json"
DEFAULT_OUTPUT = REPO_ROOT / "outputs" / "orchestration_dependency_graph.html"

ROLE_COLOURS = {
    "orchestration": "#6ca8ff",
    "integrity": "#34d399",
    "visualization": "#f59e0b",
    "synchronization": "#a78bfa",
    "observability": "#f87171",
    "recursive traversal": "#38bdf8",
}
DEFAULT_COLOUR = "#9ca3af"


def _load_topology(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_dependency_graph(topology: dict):
    try:
        import plotly.graph_objects as go
    except ImportError as exc:
        raise SystemExit(
            "Plotly is required. Install it with: pip install plotly"
        ) from exc

    root_id = topology.get("root", "ROOT")
    agents = topology.get("agents", [])

    node_ids = [root_id] + [a["id"] for a in agents]
    node_labels = [root_id] + [f"{a['id']}\n({a.get('role','?')})" for a in agents]
    node_colours = ["#fbbf24"] + [
        ROLE_COLOURS.get(a.get("role", ""), DEFAULT_COLOUR) for a in agents
    ]

    # Edges: root → every agent
    edge_x: list[float | None] = []
    edge_y: list[float | None] = []

    n = len(node_ids)
    import math

    xs = [0.0]
    ys = [0.0]
    for i, _agent in enumerate(agents):
        angle = 2 * math.pi * i / max(len(agents), 1)
        xs.append(math.cos(angle))
        ys.append(math.sin(angle))

    for i in range(1, n):
        edge_x += [xs[0], xs[i], None]
        edge_y += [ys[0], ys[i], None]

    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        mode="lines",
        line={"width": 1, "color": "#374151"},
        hoverinfo="none",
    )

    node_trace = go.Scatter(
        x=xs,
        y=ys,
        mode="markers+text",
        text=node_labels,
        textposition="top center",
        marker={
            "size": [20 if i == 0 else 14 for i in range(n)],
            "color": node_colours,
            "line": {"width": 1, "color": "#1f2937"},
        },
        hoverinfo="text",
    )

    fig = go.Figure(
        data=[edge_trace, node_trace],
        layout=go.Layout(
            title="Orchestration Dependency Graph — A7 Agent Topology",
            showlegend=False,
            xaxis={"showgrid": False, "zeroline": False, "showticklabels": False},
            yaxis={"showgrid": False, "zeroline": False, "showticklabels": False},
            plot_bgcolor="#111827",
            paper_bgcolor="#0f172a",
            font={"color": "#e5e7eb"},
            margin={"l": 20, "r": 20, "t": 60, "b": 20},
        ),
    )
    return fig


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate orchestration dependency graph.")
    parser.add_argument("--topology", type=Path, default=DEFAULT_TOPOLOGY)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)

    if not args.topology.exists():
        print(f"FAIL: topology file not found: {args.topology}")
        return 1

    topology = _load_topology(args.topology)
    fig = build_dependency_graph(topology)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(str(args.output))
    print(f"generated {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
