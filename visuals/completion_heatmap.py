import plotly.graph_objects as go

categories = [
    'Governance',
    'Rendering',
    'Validation',
    'Orchestration',
    'Thermodynamics',
    'Publication',
]

status_values = [[95,82,61,73,38,57]]

fig = go.Figure(
    data=go.Heatmap(
        z=status_values,
        x=categories,
        y=['Completion'],
    )
)

fig.update_layout(
    title='ABACUS_RENDER_PIPELINE Completion Heatmap',
)

fig.write_html('outputs/completion_heatmap.html')
print('generated outputs/completion_heatmap.html')
