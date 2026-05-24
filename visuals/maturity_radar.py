import plotly.graph_objects as go
from pathlib import Path
import yaml
from .metric_display import normalize_metric_name


def main() -> None:
    # Load program metrics from governed manifest
    manifest_path = Path(__file__).parent.parent / 'MANIFEST' / 'PROGRAM_METRICS.yaml'
    with manifest_path.open('r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    metrics = data['program_metrics']['metrics']
    categories = []
    values = []
    
    # Extract categories and scores in consistent order
    for key, metric in metrics.items():
        display_name = normalize_metric_name(key)
        categories.append(display_name)
        values.append(metric['score'])

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
        polar=dict(radialaxis=dict(visible=True, range=[0,100])),
        title='ABACUS_RENDER_PIPELINE Maturity Radar',
    )

    output_path = Path(__file__).resolve().parent.parent / 'outputs' / 'html' / 'maturity_radar.html'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(str(output_path))
    print(f'generated {output_path}')


if __name__ == '__main__':
    main()
