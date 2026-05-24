import plotly.graph_objects as go
from pathlib import Path
import yaml


def main() -> None:
    manifest_path = Path(__file__).parent.parent / 'MANIFEST' / 'THERMODYNAMIC_KPIS.yaml'
    with manifest_path.open('r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    kpis = data['thermodynamic_kpis']['metrics']
    metrics = [kpi['name'] for kpi in kpis]
    scores = [kpi['score'] for kpi in kpis]

    fig = go.Figure(
        data=[
            go.Bar(
                x=metrics,
                y=scores,
                name='Thermo KPI Maturity',
            )
        ]
    )

    fig.update_layout(
        title='Thermodynamic KPI Overlay',
        yaxis_title='Maturity Score',
    )

    output_path = Path(__file__).resolve().parent.parent / 'outputs' / 'html' / 'thermo_kpi_overlay.html'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(str(output_path))
    print(f'generated {output_path}')


if __name__ == '__main__':
    main()
