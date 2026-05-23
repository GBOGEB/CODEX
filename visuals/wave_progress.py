import plotly.graph_objects as go
from pathlib import Path


def main() -> None:
    waves = ['A1','A2','A3','A4','A5','A6','A7','A8']
    completion = [100,100,100,100,100,86,41,67]

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

    output_path = Path('outputs/wave_progression.html')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(str(output_path))
    print(f'generated {output_path}')


if __name__ == '__main__':
    main()
