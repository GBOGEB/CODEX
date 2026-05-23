import plotly.graph_objects as go
from pathlib import Path


def main() -> None:
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

    output_path = Path('outputs/maturity_radar.html')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(str(output_path))
    print(f'generated {output_path}')


if __name__ == '__main__':
    main()
