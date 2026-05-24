import plotly.graph_objects as go
from pathlib import Path
import yaml

MANIFEST_DIR = Path(__file__).parent.parent / 'MANIFEST'


def main() -> None:
    manifest_path = MANIFEST_DIR / 'THERMODYNAMIC_KPIS.yaml'
    try:
        with manifest_path.open('r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        kpis = data['thermodynamic_kpis']['metrics']
    except FileNotFoundError as exc:
        raise RuntimeError(f'Missing manifest: {manifest_path}') from exc
    except yaml.YAMLError as exc:
        raise RuntimeError(f'Invalid YAML in manifest: {manifest_path}') from exc
    except TypeError as exc:
        raise RuntimeError(
            'Invalid thermodynamic KPI structure in '
            f'{manifest_path} (expected metrics as a list of objects with name and score)'
        ) from exc
    except KeyError as exc:
        raise RuntimeError(
            f'Missing key "{exc.args[0]}" in thermodynamic KPI manifest: {manifest_path}'
        ) from exc

    if not isinstance(kpis, list) or any(
        not isinstance(kpi, dict) or 'name' not in kpi or 'score' not in kpi
        for kpi in kpis
    ):
        raise RuntimeError(
            'Invalid thermodynamic KPI structure in '
            f'{manifest_path} (expected metrics as a list of objects with name and score)'
        )

    metrics = [kpi['name'] for kpi in kpis]
    scores = [kpi['score'] for kpi in kpis]

    fig = go.Figure(
        data=[
            go.Bar(
                x=metrics,
                y=scores,
                name='Thermo KPI Maturity',
            )
        ]
    )

    fig.update_layout(
        title='Thermodynamic KPI Overlay',
        yaxis_title='Maturity Score',
    )

    output_path = Path(__file__).resolve().parent.parent / 'outputs' / 'html' / 'thermo_kpi_overlay.html'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(str(output_path))
    print(f'generated {output_path}')


if __name__ == '__main__':
    main()
