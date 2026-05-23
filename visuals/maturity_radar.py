from pathlib import Path
import sys

try:
    import plotly.graph_objects as go
except ImportError as e:
    print(f"Error: Missing required dependency: {e.name}")
    print("Install with: pip install plotly")
    sys.exit(1)


def generate_maturity_radar_chart(output_path: Path) -> None:
    """Generate maturity radar chart.
    
    Note: Currently uses hard-coded values. Future enhancement:
    load from MANIFEST/PROGRAM_METRICS.yaml for governed KPI tracking.
    """
    categories = [
        'Governance',
        'Renderer',
        'CI/CD',
        'Orchestration',
        'Visualization',
        'Thermodynamics',
        'Validation',
        'Publication',
    ]
    
    values = [86, 74, 62, 68, 71, 38, 52, 58]
    
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
