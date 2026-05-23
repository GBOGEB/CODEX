from pathlib import Path
import sys

try:
    import plotly.graph_objects as go
except ImportError as e:
    print(f"Error: Missing required dependency: {e.name}")
    print("Install with: pip install plotly")
    sys.exit(1)


def generate_completion_heatmap(output_path: Path) -> None:
    """Generate completion heatmap.
    
    Note: Currently uses hard-coded values. Future enhancement:
    load from MANIFEST/PROGRAM_METRICS.yaml for governed KPI tracking.
    """
    categories = [
        'Governance',
        'Rendering',
        'Validation',
        'Orchestration',
        'Thermodynamics',
        'Publication',
    ]
    
    status_values = [[95, 82, 61, 73, 38, 57]]
    
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
