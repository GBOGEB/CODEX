import plotly.graph_objects as go

waves = ['A1','A2','A3','A4','A5','A6','A7']
completion = [100,100,100,100,100,86,41]

fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=waves,
        y=completion,
        mode='lines+markers',
        name='Wave Completion %',
    )
)

fig.update_layout(
    title='ABACUS_RENDER_PIPELINE Wave Progression',
    xaxis_title='Wave',
    yaxis_title='Completion %',
)

fig.write_html('outputs/wave_progression.html')
print('generated outputs/wave_progression.html')
