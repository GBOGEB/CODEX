from pathlib import Path

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

scores = [34,41,27,43,18,12,9,6]

def build_thermo_kpi_overlay():
    try:
        import plotly.graph_objects as go
    except ImportError as exc:
        raise SystemExit(
            'Plotly is required to generate thermo KPI overlay. Install it with: pip install plotly'
        ) from exc

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
    return fig


def main():
    output_path = Path('outputs/thermo_kpi_overlay.html')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig = build_thermo_kpi_overlay()
    fig.write_html(str(output_path))
    print(f'generated {output_path}')


if __name__ == '__main__':
    main()
