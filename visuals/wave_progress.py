from pathlib import Path
import sys

try:
    import plotly.graph_objects as go
    import yaml
except ImportError as e:
    print(f"Error: Missing required dependency: {e.name}")
    print("Install with: pip install plotly pyyaml")
    sys.exit(1)


def load_wave_progression(manifest_path: Path) -> tuple[list[str], list[int]]:
    """Load wave progression data from YAML manifest."""
    if not manifest_path.exists():
        raise FileNotFoundError(
            f"Wave progression manifest not found: {manifest_path}\n"
            f"Expected MANIFEST/WAVE_PROGRESSION.yaml in repository root."
        )
    
    with open(manifest_path) as f:
        data = yaml.safe_load(f)
    
    waves = []
    completion = []
    
    for wave_entry in data.get('waves', []):
        waves.append(wave_entry['wave'])
        completion.append(wave_entry['completion'])
    
    return waves, completion


def generate_wave_progression_chart(output_path: Path) -> None:
    """Generate wave progression chart from governed manifest."""
    # Resolve manifest path relative to repo root
    repo_root = Path(__file__).parent.parent
    manifest_path = repo_root / 'MANIFEST' / 'WAVE_PROGRESSION.yaml'
    
    waves, completion = load_wave_progression(manifest_path)
    
    fig = go.Figure()
    
    fig.add_trace(
        go.Scatter(
            x=waves,
            y=completion,
            mode='lines+markers',
            name='Wave Completion %',
        )
    )
    
    fig.update_layout(
        title='ABACUS_RENDER_PIPELINE Wave Progression',
        xaxis_title='Wave',
        yaxis_title='Completion %',
    )
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    fig.write_html(str(output_path))
    print(f'generated {output_path}')


def main() -> None:
    """Main entry point for wave progression visualization."""
    repo_root = Path(__file__).parent.parent
    output_path = repo_root / 'outputs' / 'html' / 'wave_progression.html'
    generate_wave_progression_chart(output_path)


if __name__ == '__main__':
    main()
