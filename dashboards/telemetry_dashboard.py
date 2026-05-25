import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
import yaml
import sys

def _import_metric_display_helpers():
    try:
        from visuals.metric_display import (
            normalize_metric_name,
            abbreviate_metric_name,
        )
    except ModuleNotFoundError as exc:
        if exc.name != 'visuals':
            raise

        _repo_root = Path(__file__).parent.parent
        if str(_repo_root) not in sys.path:
            sys.path.insert(0, str(_repo_root))

        from visuals.metric_display import (
            normalize_metric_name,
            abbreviate_metric_name,
        )
    return normalize_metric_name, abbreviate_metric_name


def main() -> None:
    normalize_metric_name, abbreviate_metric_name = _import_metric_display_helpers()

    # Load wave progression from governed manifest
    wave_manifest_path = Path(__file__).parent.parent / 'MANIFEST' / 'WAVE_PROGRESSION.yaml'
    with wave_manifest_path.open('r', encoding='utf-8') as f:
        wave_data = yaml.safe_load(f)
    
    # Load program metrics from governed manifest
    metrics_manifest_path = Path(__file__).parent.parent / 'MANIFEST' / 'PROGRAM_METRICS.yaml'
    with metrics_manifest_path.open('r', encoding='utf-8') as f:
        metrics_data = yaml.safe_load(f)
    
    # Extract wave data
    waves = [w['wave'] for w in wave_data['waves']]
    completion = [w['completion'] for w in wave_data['waves']]
    wave_metrics = wave_data['wave_metrics']
    thermo = [wave_metrics['thermodynamic_progress'][w] for w in waves]
    publication = [wave_metrics['publication_progress'][w] for w in waves]
    governance = [wave_metrics['renderer_governance_progress'][w] for w in waves]
    
    # Extract program metrics
    metrics = metrics_data['program_metrics']['metrics']
    radar_categories = []
    radar_values = []
    heatmap_categories = []
    heatmap_values = []
    
    for key, metric in metrics.items():
        display_name = normalize_metric_name(key)
        abbrev = abbreviate_metric_name(display_name)
        
        radar_categories.append(display_name)
        radar_values.append(metric['score'])
        heatmap_categories.append(abbrev)
        heatmap_values.append(metric['score'])

    fig = make_subplots(
        rows=2,
        cols=2,
        specs=[[{'type':'xy'}, {'type':'polar'}],
               [{'type':'heatmap'}, {'type':'scene'}]],
        subplot_titles=(
            'Wave Completion Progression',
            'Maturity Radar',
            'Program Metrics Heatmap',
            'Convergence Surface',
        ),
    )

    fig.add_trace(
        go.Scatter(x=waves, y=completion, mode='lines+markers', name='Completion %'),
        row=1,
        col=1,
    )
    
    # Add y-axis title for wave completion
    fig.update_yaxes(title_text='Completion %', row=1, col=1)
    fig.update_xaxes(title_text='Wave', row=1, col=1)

    fig.add_trace(
        go.Scatterpolar(
            r=radar_values,
            theta=radar_categories,
            fill='toself',
            name='Maturity Radar',
        ),
        row=1,
        col=2,
    )

    fig.add_trace(
        go.Heatmap(
            z=[heatmap_values],
            x=heatmap_categories,
            y=['Score'],
        ),
        row=2,
        col=1,
    )

    fig.add_trace(
        go.Scatter3d(
            x=governance,
            y=publication,
            z=thermo,
            mode='lines+markers',
            name='Convergence Surface',
        ),
        row=2,
        col=2,
    )

    fig.update_layout(
        title='ABACUS_RENDER_PIPELINE Command Center',
        height=900,
    )

    output_path = Path(__file__).resolve().parent.parent / 'outputs' / 'html' / 'telemetry_dashboard.html'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(str(output_path))
    print(f'generated {output_path}')


if __name__ == '__main__':
    main()
