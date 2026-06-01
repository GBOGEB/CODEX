from pathlib import Path

import yaml


def load_wave_progression(manifest_path: Path) -> tuple[list[str], list[float]]:
    if not manifest_path.exists():
        raise FileNotFoundError(manifest_path)
    payload = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("WAVE_PROGRESSION manifest must be a mapping")
    waves_payload = payload.get("waves")
    if not isinstance(waves_payload, list):
        raise ValueError('"waves" must be a list')

    waves: list[str] = []
    completion: list[float] = []
    for index, item in enumerate(waves_payload):
        if not isinstance(item, dict):
            raise ValueError(f"waves[{index}] must be a mapping")
        if "wave" not in item or "completion" not in item:
            raise ValueError(f"waves[{index}] must include wave and completion")
        score = item["completion"]
        if isinstance(score, bool) or not isinstance(score, (int, float)):
            raise ValueError(f"waves[{index}].completion must be numeric")
        score = float(score)
        if not 0 <= score <= 100:
            raise ValueError("Wave completion must be within [0, 100]")
        waves.append(str(item["wave"]))
        completion.append(score)
    return waves, completion


def build_wave_progress_figure(manifest_path: Path = Path("MANIFEST/WAVE_PROGRESSION.yaml")):
    try:
        import plotly.graph_objects as go
    except ImportError as exc:
        raise SystemExit(
            'Plotly is required to generate wave progress. Install it with: pip install plotly'
        ) from exc

    fig = go.Figure()
    waves, completion = load_wave_progression(manifest_path)

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
