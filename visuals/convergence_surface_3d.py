import plotly.graph_objects as go
from pathlib import Path
import yaml


def main() -> None:
    # Load wave metrics from governed manifest
    manifest_path = Path(__file__).parent.parent / 'MANIFEST' / 'WAVE_PROGRESSION.yaml'
    with open(manifest_path, 'r') as f:
        data = yaml.safe_load(f)
    
    waves = [w['wave'] for w in data['waves']]
    wave_metrics = data['wave_metrics']
    governance = [wave_metrics['renderer_governance_progress'][w] for w in waves]
    thermo = [wave_metrics['thermodynamic_progress'][w] for w in waves]
    publication = [wave_metrics['publication_progress'][w] for w in waves]

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
