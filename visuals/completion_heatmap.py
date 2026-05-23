import plotly.graph_objects as go
from pathlib import Path


def main() -> None:
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

    output_path = Path('outputs/completion_heatmap.html')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(str(output_path))
    print(f'generated {output_path}')


if __name__ == '__main__':
    main()
