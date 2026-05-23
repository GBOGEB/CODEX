import plotly.graph_objects as go

backends = ['Fallback','NIST','CoolProp','REFPROP','HEPAK']

residuals = [
    [0.0,0.12,0.34,0.48,0.57],
    [0.12,0.0,0.18,0.31,0.41],
    [0.34,0.18,0.0,0.16,0.28],
    [0.48,0.31,0.16,0.0,0.19],
    [0.57,0.41,0.28,0.19,0.0],
]

fig = go.Figure(
    data=go.Heatmap(
        z=residuals,
        x=backends,
        y=backends,
    )
)

fig.update_layout(
    title='Backend Residual Heatmap (A9 Scaffold)',
)

fig.write_html('outputs/backend_residual_heatmap.html')
print('generated outputs/backend_residual_heatmap.html')
