import plotly.graph_objects as go

waves = ['A1','A2','A3','A4','A5','A6','A7','A8','A9']
governance = [18,35,49,63,74,88,92,94,95]
thermo = [2,4,9,14,22,31,38,44,52]
publication = [8,22,35,48,61,76,83,88,91]

fig = go.Figure(
    data=[
        go.Scatter3d(
            x=governance,
            y=publication,
            z=thermo,
            mode='lines+markers+text',
            text=waves,
            name='Wave Convergence',
        )
    ]
)

fig.update_layout(
    title='A9 Convergence Topology Surface',
    scene=dict(
        xaxis_title='Governance',
        yaxis_title='Publication',
        zaxis_title='Thermodynamics',
    ),
)

fig.write_html('outputs/convergence_surface_3d.html')
print('generated outputs/convergence_surface_3d.html')
