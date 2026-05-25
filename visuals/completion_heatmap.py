import sys
from pathlib import Path

# Ensure repo root is on sys.path so that visuals.* imports work when
# this script is executed directly (python visuals/completion_heatmap.py).
_REPO_ROOT = str(Path(__file__).parent.parent)
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from visuals.program_metrics_manifest import load_program_metric_entries, metric_display_label


def load_completion_metrics(manifest_path: Path) -> tuple[list[str], list[list[float]]]:
    """Load completion metrics from governed YAML manifest."""
    entries = load_program_metric_entries(manifest_path)
    categories = [metric_display_label(name, data) for name, data in entries]
    values = [float(data['score']) for _, data in entries]
    return categories, [values]


def generate_completion_heatmap(output_path: Path) -> None:
    """Generate completion heatmap from governed manifest."""
    try:
        import plotly.graph_objects as go
    except ImportError as e:
        raise ImportError(
            f"Missing required dependency: {e.name}\n"
            "Install with: pip install plotly"
        ) from e
    
    repo_root = Path(__file__).parent.parent
    manifest_path = repo_root / 'MANIFEST' / 'PROGRAM_METRICS.yaml'
    categories, status_values = load_completion_metrics(manifest_path)
    
    fig = go.Figure(
        data=go.Heatmap(
            z=status_values,
            x=categories,
            y=['Completion'],
        )
    )
    
    fig.update_layout(
        title='ABACUS_RENDER_PIPELINE Completion Heatmap',
    )
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    fig.write_html(str(output_path))
    print(f'generated {output_path}')


def main() -> None:
    """Main entry point for completion heatmap visualization."""
    repo_root = Path(__file__).parent.parent
    output_path = repo_root / 'outputs' / 'html' / 'completion_heatmap.html'
    generate_completion_heatmap(output_path)


if __name__ == '__main__':
    main()
