"""A9 Thermodynamic Command Center dashboard.

Reads backend availability from physics/backend_registry.yaml and
wave metrics from MANIFEST/THERMODYNAMIC_KPIS.yaml and
MANIFEST/WAVE_PROGRESSION.yaml rather than hard-coding values.
"""
from __future__ import annotations

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
BACKEND_REGISTRY = REPO_ROOT / "physics" / "backend_registry.yaml"
THERMO_KPIS = REPO_ROOT / "MANIFEST" / "THERMODYNAMIC_KPIS.yaml"
WAVE_PROGRESSION = REPO_ROOT / "MANIFEST" / "WAVE_PROGRESSION.yaml"
OUTPUT_PATH = REPO_ROOT / "outputs" / "thermo_command_center.html"

# Fixed residual matrix — consistent with backend_residual_heatmap.py (5 backends)
_BACKEND_ORDER = ["Fallback", "NIST", "CoolProp", "REFPROP", "HEPAK"]
_RESIDUAL_MATRIX = [
    [0.00, 0.12, 0.34, 0.48, 0.57],
    [0.12, 0.00, 0.18, 0.31, 0.41],
    [0.34, 0.18, 0.00, 0.16, 0.28],
    [0.48, 0.31, 0.16, 0.00, 0.19],
    [0.57, 0.41, 0.28, 0.19, 0.00],
]


def _load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _load_thermo_kpi_data() -> tuple[list[str], list[int]]:
    if not THERMO_KPIS.exists():
        return ["Entropy", "Density", "JT", "NIST"], [34, 41, 27, 43]
    data = _load_yaml(THERMO_KPIS)
    metrics = data.get("thermodynamic_kpis", {}).get("metrics", [])
    names = [m["name"] for m in metrics]
    scores = [m["score"] for m in metrics]
    return names, scores


def _load_wave_progression() -> tuple[list[str], list[int], list[int], list[int]]:
    if not WAVE_PROGRESSION.exists():
        waves = ["A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9"]
        return (
            waves,
            [18, 35, 49, 63, 74, 88, 92, 94, 95],
            [8, 22, 35, 48, 61, 76, 83, 88, 91],
            [2, 4, 9, 14, 22, 31, 38, 44, 52],
        )
    data = _load_yaml(WAVE_PROGRESSION)
    metrics = data.get("wave_metrics", {})
    renderer_map = metrics.get("renderer_governance_progress", {}) or {}
    publication_map = metrics.get("publication_progress", {}) or {}
    thermo_map = metrics.get("thermodynamic_progress", {}) or {}

    waves: list[str] = list(renderer_map.keys())
    for wave in publication_map:
        if wave not in waves:
            waves.append(wave)
    for wave in thermo_map:
        if wave not in waves:
            waves.append(wave)

    renderer = [int(renderer_map.get(wave, 0)) for wave in waves]
    publication = [int(publication_map.get(wave, 0)) for wave in waves]
    thermo = [int(thermo_map.get(wave, 0)) for wave in waves]
    return waves, renderer, publication, thermo


def _load_backend_labels() -> list[str]:
    if not BACKEND_REGISTRY.exists():
        return _BACKEND_ORDER
    data = _load_yaml(BACKEND_REGISTRY)
    order = []
    for name in _BACKEND_ORDER:
        cfg = data.get("backends", {}).get(name.lower(), {})
        label = name if cfg.get("available", False) else f"{name}*"
        order.append(label)
    return order


def build_command_center():
    try:
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
    except ImportError as exc:
        raise SystemExit(
            "Plotly is required. Install it with: pip install plotly"
        ) from exc

    kpi_names, kpi_scores = _load_thermo_kpi_data()
    waves, renderer_prog, pub_prog, thermo_prog = _load_wave_progression()
    backend_labels = _load_backend_labels()

    fig = make_subplots(
        rows=2,
        cols=2,
        specs=[
            [{"type": "heatmap"}, {"type": "bar"}],
            [{"type": "scatter3d"}, {"type": "scatter"}],
        ],
        subplot_titles=(
            "Backend Residuals (* = unavailable)",
            "Thermo KPI Overlay",
            "Scientific Convergence (A1-A9)",
            "Confidence Progression (A1-A9)",
        ),
    )

    fig.add_trace(
        go.Heatmap(
            z=_RESIDUAL_MATRIX,
            x=backend_labels,
            y=backend_labels,
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Bar(x=kpi_names, y=kpi_scores, name="Thermo KPIs"),
        row=1,
        col=2,
    )

    fig.add_trace(
        go.Scatter3d(
            x=renderer_prog,
            y=pub_prog,
            z=thermo_prog,
            mode="lines+markers",
            name="Scientific Convergence",
        ),
        row=2,
        col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=waves,
            y=thermo_prog,
            mode="lines+markers",
            name="Scientific Confidence",
        ),
        row=2,
        col=2,
    )

    fig.update_layout(title="A9 Thermodynamic Command Center", height=950)
    return fig


def main() -> int:
    fig = build_command_center()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(str(OUTPUT_PATH))
    print(f"generated {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())