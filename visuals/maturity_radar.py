from pathlib import Path


def load_program_metrics(manifest_path: Path) -> tuple[list[str], list[float]]:
    """Load maturity metrics from governed YAML manifest."""
    try:
        import yaml
    except ImportError as e:
        raise ImportError(
            f"Missing required dependency: {e.name}\n"
            "Install with: pip install pyyaml"
        ) from e
    
    if not manifest_path.exists():
        raise FileNotFoundError(
            f"Program metrics manifest not found: {manifest_path}\n"
            f"Expected MANIFEST/PROGRAM_METRICS.yaml in repository root."
        )

    with open(manifest_path, encoding='utf-8') as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict):
        raise ValueError(
            'Invalid program metrics manifest schema: expected top-level mapping.'
        )

    program_metrics = data.get('program_metrics')
    if not isinstance(program_metrics, dict):
        raise ValueError(
            'Invalid program metrics manifest schema: expected "program_metrics" mapping.'
        )

    metrics = program_metrics.get('metrics')
    if not isinstance(metrics, dict) or not metrics:
        raise ValueError(
            'Invalid program metrics manifest schema: expected non-empty "metrics" mapping.'
        )

    categories: list[str] = []
    values: list[float] = []
    for metric_name, metric_data in metrics.items():
        if not isinstance(metric_data, dict):
            raise ValueError(
                f'Invalid program metrics manifest schema at metrics.{metric_name}: '
                'expected mapping containing "score".'
            )
        score = metric_data.get('score')
        if not isinstance(score, (int, float)):
            raise ValueError(
                f'Invalid program metrics manifest schema at metrics.{metric_name}.score: '
                'expected number.'
            )

        categories.append(metric_name.replace('_', ' ').title())
        values.append(float(score))

    return categories, values


def generate_maturity_radar_chart(output_path: Path) -> None:
    """Generate maturity radar chart from governed manifest."""
    try:
        import plotly.graph_objects as go
    except ImportError as e:
        raise ImportError(
            f"Missing required dependency: {e.name}\n"
            "Install with: pip install plotly"
        ) from e
    
    repo_root = Path(__file__).parent.parent
    manifest_path = repo_root / 'MANIFEST' / 'PROGRAM_METRICS.yaml'
    categories, values = load_program_metrics(manifest_path)
    
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
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        title='ABACUS_RENDER_PIPELINE Maturity Radar',
    )
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    fig.write_html(str(output_path))
    print(f'generated {output_path}')


def main() -> None:
    """Main entry point for maturity radar visualization."""
    repo_root = Path(__file__).parent.parent
    output_path = repo_root / 'outputs' / 'html' / 'maturity_radar.html'
    generate_maturity_radar_chart(output_path)


if __name__ == '__main__':
    main()
