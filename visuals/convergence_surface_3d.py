import plotly.graph_objects as go
from pathlib import Path
import yaml

waves = ['A1','A2','A3','A4','A5','A6','A7','A8','A9']
governance = [18,35,49,63,74,88,92,94,95]
thermo = [2,4,9,14,22,31,38,44,52]
publication = [8,22,35,48,61,76,83,88,91]

def main() -> None:
    # Load wave metrics from governed manifest
    manifest_path = Path(__file__).parent.parent / 'MANIFEST' / 'WAVE_PROGRESSION.yaml'
    with manifest_path.open('r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    waves = [w['wave'] for w in data['waves']]
    wave_metrics = data['wave_metrics']
    governance = [wave_metrics['renderer_governance_progress'][w] for w in waves]
    thermo = [wave_metrics['thermodynamic_progress'][w] for w in waves]
    publication = [wave_metrics['publication_progress'][w] for w in waves]

fig.update_layout(
    title='A9 Convergence Topology Surface',
    scene=dict(
        xaxis_title='Governance',
        yaxis_title='Publication',
        zaxis_title='Thermodynamics',
    ),
)

    fig.update_layout(
        title='A8 Convergence Topology Surface',
        scene=dict(
            xaxis_title='Governance',
            yaxis_title='Publication',
            zaxis_title='Thermodynamics',
        ),
    )

    output_path = Path(__file__).resolve().parent.parent / 'outputs' / 'html' / 'convergence_surface_3d.html'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(str(output_path))
    print(f'generated {output_path}')


if __name__ == '__main__':
    main()
