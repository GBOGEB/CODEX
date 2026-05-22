import plotly.graph_objects as go

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

fig.write_html('outputs/thermo_kpi_overlay.html')
print('generated outputs/thermo_kpi_overlay.html')
