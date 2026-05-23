import plotly.graph_objects as go
from pathlib import Path


def main() -> None:
    waves = ['A1','A2','A3','A4','A5','A6','A7','A8']
    governance = [18,35,49,63,74,88,92,94]
    thermo = [2,4,9,14,22,31,38,44]
    publication = [8,22,35,48,61,76,83,88]

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
        title='A8 Convergence Topology Surface',
        scene=dict(
            xaxis_title='Governance',
            yaxis_title='Publication',
            zaxis_title='Thermodynamics',
        ),
    )

    output_path = Path('outputs/convergence_surface_3d.html')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(str(output_path))
    print(f'generated {output_path}')


if __name__ == '__main__':
    main()
