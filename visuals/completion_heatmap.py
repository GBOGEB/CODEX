import plotly.graph_objects as go
from pathlib import Path
import yaml
import sys

# Handle both package import and standalone script execution
try:
    from .metric_display import normalize_metric_name
except ImportError:
    # Running as standalone script - add parent to path
    _script_dir = Path(__file__).parent
    if str(_script_dir) not in sys.path:
        sys.path.insert(0, str(_script_dir))
    from metric_display import normalize_metric_name


def main() -> None:
    # Load program metrics from governed manifest
    manifest_path = Path(__file__).parent.parent / 'MANIFEST' / 'PROGRAM_METRICS.yaml'
    with manifest_path.open('r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    metrics = data['program_metrics']['metrics']
    categories = []
    status_values = []
    
    # Extract categories and scores
    for key, metric in metrics.items():
        display_name = normalize_metric_name(key)
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

    output_path = Path(__file__).resolve().parent.parent / 'outputs' / 'html' / 'completion_heatmap.html'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(str(output_path))
    print(f'generated {output_path}')


if __name__ == '__main__':
    main()
