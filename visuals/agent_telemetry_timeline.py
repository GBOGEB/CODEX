"""Generate an agent telemetry timeline from agent_runtime/agent_metrics.json.

Reads per-agent completion scores and runtime targets and produces a
Plotly bar timeline HTML artifact.

Usage:
    python visuals/agent_telemetry_timeline.py [--metrics PATH] [--output PATH]
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_METRICS = REPO_ROOT / "agent_runtime" / "agent_metrics.json"
DEFAULT_OUTPUT = REPO_ROOT / "outputs" / "agent_telemetry_timeline.html"


def _load_metrics(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_telemetry_figure(metrics: dict):
    try:
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
    except ImportError as exc:
        raise SystemExit(
            "Plotly is required. Install it with: pip install plotly"
        ) from exc

    agents = metrics.get("agents", {})
    agent_names = list(agents.keys())
    agent_scores = [agents[a] for a in agent_names]

    runtime_targets = metrics.get("runtime_targets", {})
    target_names = list(runtime_targets.keys())
    target_values = [runtime_targets[t] for t in target_names]

    wave = metrics.get("wave", "?")
    arch_before = metrics.get("architecture_score_before", 0)
    arch_target = metrics.get("architecture_score_target", 0)
    completion = metrics.get("completion_percent", 0)

    fig = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=("Agent Completion Scores (%)", "Runtime Targets (%)"),
    )

    fig.add_trace(
        go.Bar(
            x=agent_names,
            y=agent_scores,
            name="Agent Completion",
            marker_color="#6ca8ff",
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Bar(
            x=target_names,
            y=target_values,
            name="Runtime Targets",
            marker_color="#34d399",
        ),
        row=1,
        col=2,
    )

    fig.update_layout(
        title=(
            f"A7 Agent Telemetry — {wave} | "
            f"Architecture: {arch_before}→{arch_target} | "
            f"Overall Completion: {completion}%"
        ),
        showlegend=False,
        plot_bgcolor="#111827",
        paper_bgcolor="#0f172a",
        font={"color": "#e5e7eb"},
        yaxis={"range": [0, 100], "title": "%"},
        yaxis2={"range": [0, 100], "title": "%"},
    )
    return fig


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate agent telemetry timeline.")
    parser.add_argument("--metrics", type=Path, default=DEFAULT_METRICS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)

    if not args.metrics.exists():
        print(f"FAIL: metrics file not found: {args.metrics}")
        return 1

    metrics = _load_metrics(args.metrics)
    fig = build_telemetry_figure(metrics)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(str(args.output))
    print(f"generated {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
