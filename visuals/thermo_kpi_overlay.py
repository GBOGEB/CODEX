import plotly.graph_objects as go
from pathlib import Path


def main() -> None:
    metrics = [
        'Entropy',
        'Density',
        'JT',
        'NIST',
        'CoolProp',
        'REFPROP',
        'HEPAK',
        'He-II',
    ]

    scores = [34, 41, 27, 43, 18, 12, 9, 6]

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
