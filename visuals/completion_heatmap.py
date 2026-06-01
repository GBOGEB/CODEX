from pathlib import Path

import yaml


def _label_from_key(key: str) -> str:
    if key.lower() == "ci_cd":
        return "CI/CD"
    return key.replace("_", " ").title()


def load_completion_metrics(manifest_path: Path) -> tuple[list[str], list[list[float]]]:
    if not manifest_path.exists():
        raise FileNotFoundError(manifest_path)
    payload = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("PROGRAM_METRICS manifest must be a mapping")
    program_metrics = payload.get("program_metrics")
    if not isinstance(program_metrics, dict):
        raise ValueError('"program_metrics" must be a mapping')
    metrics = program_metrics.get("metrics")
    if not isinstance(metrics, dict):
        raise ValueError('"metrics" must be a mapping')

    categories: list[str] = []
    values: list[float] = []
    for key, item in metrics.items():
        if not isinstance(item, dict):
            raise ValueError(f"Metric '{key}' must be a mapping")
        score = item.get("score")
        if isinstance(score, bool) or not isinstance(score, (int, float)):
            raise ValueError(f"Metric '{key}' score must be numeric")
        score = float(score)
        if not 0 <= score <= 100:
            raise ValueError("Metric scores must be within [0, 100]")
        label = item.get("label")
        categories.append(label if isinstance(label, str) and label else _label_from_key(str(key)))
        values.append(score)

    return categories, [values]


def build_completion_heatmap(manifest_path: Path = Path("MANIFEST/PROGRAM_METRICS.yaml")):
    try:
        import plotly.graph_objects as go
    except ImportError as exc:
        raise SystemExit(
            'Plotly is required to generate completion heatmap. Install it with: pip install plotly'
        ) from exc

    categories, status_values = load_completion_metrics(manifest_path)
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
