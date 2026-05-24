from pathlib import Path
import sys

try:
    import plotly.graph_objects as go
    import yaml
except ImportError as e:
    print(f"Error: Missing required dependency: {e.name}")
    print("Install with: pip install plotly pyyaml")
    sys.exit(1)


def load_wave_progression(manifest_path: Path) -> tuple[list[str], list[float]]:
    """Load wave progression data from YAML manifest."""
    if not manifest_path.exists():
        raise FileNotFoundError(
            f"Wave progression manifest not found: {manifest_path}\n"
            f"Expected MANIFEST/WAVE_PROGRESSION.yaml in repository root."
        )
    
    with open(manifest_path, encoding='utf-8') as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict):
        raise ValueError(
            'Invalid wave progression manifest schema: expected a mapping with a "waves" list.'
        )

    wave_entries = data.get('waves')
    if not isinstance(wave_entries, list):
        raise ValueError(
            'Invalid wave progression manifest schema: expected "waves" to be a list of '
            'objects with "wave" and "completion" keys.'
        )

    waves = []
    completion = []

    for index, wave_entry in enumerate(wave_entries):
        if not isinstance(wave_entry, dict):
            raise ValueError(
                f'Invalid wave progression manifest schema at waves[{index}]: expected mapping.'
            )

        if 'wave' not in wave_entry or 'completion' not in wave_entry:
            raise ValueError(
                f'Invalid wave progression manifest schema at waves[{index}]: '
                'required keys are "wave" and "completion".'
            )

        wave = wave_entry['wave']
        completion_value = wave_entry['completion']

        if not isinstance(wave, str) or not wave.strip():
            raise ValueError(
                f'Invalid wave progression manifest schema at waves[{index}].wave: '
                'expected non-empty string.'
            )
        if not isinstance(completion_value, (int, float)):
            raise ValueError(
                f'Invalid wave progression manifest schema at waves[{index}].completion: '
                'expected number.'
            )

        waves.append(wave)
        completion.append(float(completion_value))
    
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
