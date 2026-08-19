from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MANIFEST_PATH = ROOT / "MANIFEST" / "WAVE_PROGRESSION.yaml"
DEFAULT_OUTPUT_PATH = ROOT / "outputs" / "html" / "convergence_surface_3d.html"


def _metric_series(
    wave_metrics: dict[str, Any],
    metric_name: str,
    waves: list[str],
) -> list[float]:
    metric_payload = wave_metrics.get(metric_name)
    if not isinstance(metric_payload, dict):
        raise ValueError(f"wave_metrics.{metric_name} must be a mapping")

    values: list[float] = []
    for wave in waves:
        value = metric_payload.get(wave)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"wave_metrics.{metric_name}.{wave} must be numeric")
        values.append(float(value))
    return values


def load_convergence_metrics(
    manifest_path: Path = DEFAULT_MANIFEST_PATH,
) -> tuple[list[str], list[float], list[float], list[float]]:
    if not manifest_path.exists():
        raise FileNotFoundError(manifest_path)

    with manifest_path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)

    if not isinstance(payload, dict):
        raise ValueError("WAVE_PROGRESSION manifest must be a mapping")

    waves_payload = payload.get("waves")
    if not isinstance(waves_payload, list):
        raise ValueError('"waves" must be a list')

    waves: list[str] = []
    for index, item in enumerate(waves_payload):
        if not isinstance(item, dict) or "wave" not in item:
            raise ValueError(f"waves[{index}] must include wave")
        waves.append(str(item["wave"]))

    wave_metrics = payload.get("wave_metrics")
    if not isinstance(wave_metrics, dict):
        raise ValueError('"wave_metrics" must be a mapping')

    governance = _metric_series(wave_metrics, "renderer_governance_progress", waves)
    thermodynamics = _metric_series(wave_metrics, "thermodynamic_progress", waves)
    publication = _metric_series(wave_metrics, "publication_progress", waves)
    return waves, governance, publication, thermodynamics


def build_convergence_surface_figure(manifest_path: Path = DEFAULT_MANIFEST_PATH):
    try:
        import plotly.graph_objects as go
    except ImportError as exc:
        raise SystemExit(
            "Plotly is required to generate the convergence surface. "
            "Install it with: pip install plotly"
        ) from exc

    waves, governance, publication, thermodynamics = load_convergence_metrics(manifest_path)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter3d(
            x=governance,
            y=publication,
            z=thermodynamics,
            mode="lines+markers+text",
            text=waves,
            textposition="top center",
            name="Wave convergence path",
            hovertemplate=(
                "Wave %{text}<br>"
                "Governance: %{x:.1f}%<br>"
                "Publication: %{y:.1f}%<br>"
                "Thermodynamics: %{z:.1f}%<extra></extra>"
            ),
        )
    )
    fig.add_trace(
        go.Mesh3d(
            x=governance,
            y=publication,
            z=thermodynamics,
            opacity=0.2,
            name="Convergence surface",
            hoverinfo="skip",
            showscale=False,
        )
    )

    fig.update_layout(
        title="A9 Convergence Topology Surface",
        scene=dict(
            xaxis_title="Governance",
            yaxis_title="Publication",
            zaxis_title="Thermodynamics",
        ),
    )
    return fig


def main() -> None:
    output_path = DEFAULT_OUTPUT_PATH
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig = build_convergence_surface_figure()
    fig.write_html(str(output_path))
    print(f"generated {output_path}")


if __name__ == "__main__":
    main()
