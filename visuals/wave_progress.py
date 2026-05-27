from pathlib import Path


def build_wave_progress_figure():
    try:
        import plotly.graph_objects as go
    except ImportError as exc:
        raise SystemExit(
            'Plotly is required to generate wave progress. Install it with: pip install plotly'
        ) from exc

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
    return fig


def main():
    output_path = Path('outputs/wave_progression.html')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig = build_wave_progress_figure()
    fig.write_html(str(output_path))
    print(f'generated {output_path}')


if __name__ == '__main__':
    main()
