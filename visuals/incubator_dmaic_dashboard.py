"""Generate an INCUBATOR DMAIC phase dashboard.

Reads all session tuples from incubator/, resolves each to a DMAIC phase
via maps/dmaic_phase_map.yml, and produces a Plotly bar/scatter timeline
grouped by DMAIC phase and coloured by category.

Usage:
    python visuals/incubator_dmaic_dashboard.py [--incubator PATH] [--map PATH] [--output PATH]
"""
from __future__ import annotations

import argparse
from pathlib import Path

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required. Install it with: pip install pyyaml") from exc

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_INCUBATOR = REPO_ROOT / "incubator"
DEFAULT_MAP = REPO_ROOT / "maps" / "dmaic_phase_map.yml"
DEFAULT_OUTPUT = REPO_ROOT / "outputs" / "incubator_dmaic_dashboard.html"

DMAIC_ORDER = ["DEFINE", "MEASURE", "ANALYZE", "IMPROVE", "CONTROL"]

PHASE_COLOURS = {
    "DEFINE":  "#6ca8ff",
    "MEASURE": "#34d399",
    "ANALYZE": "#f59e0b",
    "IMPROVE": "#a78bfa",
    "CONTROL": "#f87171",
}

CATEGORY_MARKER = {
    "INCUBATOR":   "circle",
    "DELIVERY":    "square",
    "GOVERNANCE":  "diamond",
    "ANALYSIS":    "cross",
    "IMPROVEMENT": "triangle-up",
    "CONTROL_OPS": "star",
}


def _load_phase_map(path: Path) -> dict:
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _load_tuples(incubator_dir: Path) -> list[dict]:
    tuples = []
    tuple_files = sorted(incubator_dir.glob("*.yml")) + sorted(incubator_dir.glob("*.yaml"))
    schema_files = {"session_tuple_schema.yml", "session_tuple_schema.yaml"}
    for yml in tuple_files:
        if yml.name in schema_files:
            continue
        with open(yml, encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        if isinstance(data, dict) and "id" in data:
            tuples.append(data)
    return tuples


def _resolve_phase(t: dict, phase_map: dict) -> str:
    """Resolve a tuple to its DMAIC phase using the routing rules."""
    category = t.get("category", "")
    theme = t.get("theme", "")
    phases = phase_map.get("dmaic_phases", {})

    # Priority 1: exact category + theme match
    for phase_name, phase_def in phases.items():
        cats = phase_def.get("incubator_categories", [])
        themes = phase_def.get("incubator_themes", [])
        if category in cats and theme in themes:
            return phase_name

    # Priority 2: category match
    for phase_name, phase_def in phases.items():
        if category in phase_def.get("incubator_categories", []):
            return phase_name

    # Priority 3: theme match
    for phase_name, phase_def in phases.items():
        if theme in phase_def.get("incubator_themes", []):
            return phase_name

    # Priority 4: default
    rules = phase_map.get("routing_rules", [])
    for rule in rules:
        if rule.get("condition") == "unmatched":
            return rule.get("default_phase", "DEFINE")
    return "DEFINE"


def build_dmaic_dashboard(tuples: list[dict], phase_map: dict):
    try:
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
    except ImportError as exc:
        raise SystemExit(
            "Plotly is required. Install it with: pip install plotly"
        ) from exc

    # Annotate each tuple with its resolved phase
    for t in tuples:
        t["_phase"] = _resolve_phase(t, phase_map)

    # Group counts by phase
    phase_counts = {p: 0 for p in DMAIC_ORDER}
    for t in tuples:
        phase_counts[t["_phase"]] = phase_counts.get(t["_phase"], 0) + 1

    fig = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=(
            "Tuple Count by DMAIC Phase",
            "Tuples Timeline (date vs phase)",
        ),
        column_widths=[0.35, 0.65],
    )

    # Left panel — bar chart of counts per phase
    fig.add_trace(
        go.Bar(
            x=DMAIC_ORDER,
            y=[phase_counts[p] for p in DMAIC_ORDER],
            marker_color=[PHASE_COLOURS[p] for p in DMAIC_ORDER],
            name="Tuple count",
            text=[phase_counts[p] for p in DMAIC_ORDER],
            textposition="outside",
        ),
        row=1,
        col=1,
    )

    # Right panel — scatter: date on x-axis, phase on y-axis, colour by category
    categories_seen: set[str] = set()
    for phase in DMAIC_ORDER:
        phase_tuples = [t for t in tuples if t["_phase"] == phase]
        for t in phase_tuples:
            cat = t.get("category", "INCUBATOR")
            categories_seen.add(cat)

    for cat in sorted(categories_seen):
        cat_tuples = [t for t in tuples if t.get("category", "INCUBATOR") == cat]
        dates = [str(t.get("date", "")) for t in cat_tuples]
        phases = [t["_phase"] for t in cat_tuples]
        ids = [t.get("id", "") for t in cat_tuples]
        titles = [t.get("title", "") for t in cat_tuples]
        hover = [f"{ids[i]}<br>{titles[i]}<br>Phase: {phases[i]}" for i in range(len(cat_tuples))]

        fig.add_trace(
            go.Scatter(
                x=dates,
                y=phases,
                mode="markers",
                name=cat,
                marker=dict(
                    symbol=CATEGORY_MARKER.get(cat, "circle"),
                    size=12,
                    color=[PHASE_COLOURS.get(p, "#9ca3af") for p in phases],
                ),
                text=hover,
                hoverinfo="text",
            ),
            row=1,
            col=2,
        )

    total = len(tuples)
    phases_summary = ", ".join(
        f"{p}: {phase_counts[p]}" for p in DMAIC_ORDER if phase_counts[p] > 0
    )

    fig.update_layout(
        title=f"INCUBATOR DMAIC Dashboard — {total} tuple(s) | {phases_summary}",
        paper_bgcolor="#1e1b4b",
        plot_bgcolor="#312e81",
        font=dict(color="#e2e8f0"),
        showlegend=True,
        height=500,
    )
    fig.update_yaxes(
        categoryorder="array",
        categoryarray=DMAIC_ORDER,
        row=1,
        col=2,
    )
    return fig


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate INCUBATOR DMAIC dashboard")
    parser.add_argument("--incubator", default=str(DEFAULT_INCUBATOR))
    parser.add_argument("--map", default=str(DEFAULT_MAP))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args()

    incubator_dir = Path(args.incubator)
    map_path = Path(args.map)
    output_path = Path(args.output)

    phase_map = _load_phase_map(map_path)
    tuples = _load_tuples(incubator_dir)

    fig = build_dmaic_dashboard(tuples, phase_map)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(str(output_path))
    print(f"generated {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
