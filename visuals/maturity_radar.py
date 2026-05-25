import sys
from pathlib import Path

# Ensure repo root is on sys.path so that visuals.* imports work when
# this script is executed directly (python visuals/maturity_radar.py).
_REPO_ROOT = str(Path(__file__).parent.parent)
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from visuals.program_metrics_manifest import load_program_metric_entries, metric_display_label


def load_program_metrics(manifest_path: Path) -> tuple[list[str], list[float]]:
    """Load maturity metrics from governed YAML manifest."""
    entries = load_program_metric_entries(manifest_path)
    categories = [metric_display_label(name, data) for name, data in entries]
    values = [float(data['score']) for _, data in entries]
    return categories, values


def generate_maturity_radar_chart(output_path: Path) -> None:
    """Generate maturity radar chart from governed manifest."""
    try:
        import plotly.graph_objects as go
    except ImportError as e:
        raise ImportError(
            f"Missing required dependency: {e.name}\n"
            "Install with: pip install plotly"
        ) from e
    
    repo_root = Path(__file__).parent.parent
    manifest_path = repo_root / 'MANIFEST' / 'PROGRAM_METRICS.yaml'
    categories, values = load_program_metrics(manifest_path)
    
    fig = go.Figure()
    
    fig.add_trace(
        go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name='Program Maturity',
        )
    )
    
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        title='ABACUS_RENDER_PIPELINE Maturity Radar',
    )
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    fig.write_html(str(output_path))
    print(f'generated {output_path}')


def main() -> None:
    """Main entry point for maturity radar visualization."""
    repo_root = Path(__file__).parent.parent
    output_path = repo_root / 'outputs' / 'html' / 'maturity_radar.html'
    generate_maturity_radar_chart(output_path)


if __name__ == '__main__':
    main()
