import plotly.graph_objects as go

categories = [
    'Governance',
    'Renderer',
    'CI/CD',
    'Orchestration',
    'Visualization',
    'Thermodynamics',
    'Validation',
    'Publication',
]

values = [86,74,62,68,71,38,52,58]

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

fig.write_html('outputs/maturity_radar.html')
print('generated outputs/maturity_radar.html')
