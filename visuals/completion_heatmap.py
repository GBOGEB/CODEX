import plotly.graph_objects as go
from pathlib import Path
import yaml


def main() -> None:
    # Load program metrics from governed manifest
    manifest_path = Path(__file__).parent.parent / 'MANIFEST' / 'PROGRAM_METRICS.yaml'
    with open(manifest_path, 'r') as f:
        data = yaml.safe_load(f)
    
    metrics = data['program_metrics']['metrics']
    categories = []
    status_values = []
    
    # Extract categories and scores
    for key, metric in metrics.items():
        display_name = key.replace('_', ' ').title()
        if display_name == 'Ci Cd':
            display_name = 'CI/CD'
        elif display_name == 'Publication Readiness':
            display_name = 'Publication'
        
        categories.append(display_name)
        status_values.append(metric['score'])

    fig = go.Figure(
        data=go.Heatmap(
            z=[status_values],
            x=categories,
            y=['Maturity Score'],
        )
    )

    fig.update_layout(
        title='ABACUS_RENDER_PIPELINE Program Metrics Heatmap',
    )

    output_path = Path('outputs/completion_heatmap.html')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(str(output_path))
    print(f'generated {output_path}')


if __name__ == '__main__':
    main()
