import plotly.graph_objects as go
from plotly.subplots import make_subplots

fig = make_subplots(
    rows=2,
    cols=2,
    specs=[[{'type':'heatmap'}, {'type':'bar'}],
           [{'type':'scatter3d'}, {'type':'scatter'}]],
    subplot_titles=(
        'Backend Residuals',
        'Thermo KPI Overlay',
        'Scientific Convergence',
        'Confidence Progression',
    ),
)

fig.add_trace(
    go.Heatmap(
        z=[[0.0,0.12,0.34],[0.12,0.0,0.18],[0.34,0.18,0.0]],
        x=['Fallback','NIST','CoolProp'],
        y=['Fallback','NIST','CoolProp'],
    ),
    row=1,
    col=1,
)

fig.add_trace(
    go.Bar(
        x=['Entropy','Density','JT','NIST'],
        y=[34,41,27,43],
        name='Thermo KPIs',
    ),
    row=1,
    col=2,
)

fig.add_trace(
    go.Scatter3d(
        x=[18,35,49,63,74,88,92],
        y=[8,22,35,48,61,76,83],
        z=[2,4,9,14,22,31,38],
        mode='lines+markers',
        name='Scientific Convergence',
    ),
    row=2,
    col=1,
)

fig.add_trace(
    go.Scatter(
        x=['A1','A2','A3','A4','A5','A6','A7','A8','A9'],
        y=[2,4,7,11,18,24,31,38,52],
        mode='lines+markers',
        name='Scientific Confidence',
    ),
    row=2,
    col=2,
)

fig.update_layout(
    title='A9 Thermodynamic Command Center',
    height=950,
)

fig.write_html('outputs/thermo_command_center.html')
print('generated outputs/thermo_command_center.html')
