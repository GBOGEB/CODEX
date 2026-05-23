import plotly.graph_objects as go
from pathlib import Path
import yaml


def main() -> None:
    # Load wave progression from governed manifest
    manifest_path = Path(__file__).parent.parent / 'MANIFEST' / 'WAVE_PROGRESSION.yaml'
    with open(manifest_path, 'r') as f:
        data = yaml.safe_load(f)
    
    waves = [w['wave'] for w in data['waves']]
    completion = [w['completion'] for w in data['waves']]

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

    output_path = Path('outputs/wave_progression.html')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(str(output_path))
    print(f'generated {output_path}')


if __name__ == '__main__':
    main()
