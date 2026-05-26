from pathlib import Path

categories = [
    'Governance',
    'Rendering',
    'Validation',
    'Orchestration',
    'Thermodynamics',
    'Publication',
]

status_values = [[95,82,61,73,38,57]]

def build_completion_heatmap():
    try:
        import plotly.graph_objects as go
    except ImportError as exc:
        raise SystemExit(
            'Plotly is required to generate completion heatmap. Install it with: pip install plotly'
        ) from exc

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
    return fig


def main():
    output_path = Path('outputs/completion_heatmap.html')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig = build_completion_heatmap()
    fig.write_html(str(output_path))
    print(f'generated {output_path}')


if __name__ == '__main__':
    main()
