from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

_DEFAULT_MANIFEST = Path(__file__).resolve().parents[1] / "MANIFEST" / "WAVE_PROGRESSION.yaml"


def load_wave_progression(
    path: Path | None = None,
) -> tuple[list[str], list[float]]:
    """Load wave progression data from a ``WAVE_PROGRESSION.yaml`` manifest.

    Args:
        path: Path to the manifest file.  Defaults to
            ``MANIFEST/WAVE_PROGRESSION.yaml`` relative to the repo root.

    Returns:
        A ``(waves, completion)`` tuple where *waves* is a list of wave
        identifiers and *completion* is a list of floats in ``[0, 100]``.

    Raises:
        FileNotFoundError: If *path* does not exist.
        ValueError: If the manifest schema is invalid.
    """
    if path is None:
        path = _DEFAULT_MANIFEST

    if not path.exists():
        raise FileNotFoundError(f"Manifest not found: {path.name}")

    raw: Any = yaml.safe_load(path.read_text(encoding="utf-8"))

    if not isinstance(raw, dict):
        raise ValueError(
            f"Expected a mapping at root of {path.name}, got {type(raw).__name__}"
        )

    entries = raw.get("waves")
    if not isinstance(entries, list):
        raise ValueError(f'Key "waves" must be a list in {path.name}')

    waves: list[str] = []
    completion: list[float] = []

    for i, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise ValueError(
                f"waves[{i}] must be a mapping, got {type(entry).__name__}"
            )
        if "wave" not in entry or "completion" not in entry:
            missing = [k for k in ("wave", "completion") if k not in entry]
            raise ValueError(
                f"waves[{i}] missing required key(s): {missing}"
            )
        raw_val = entry["completion"]
        try:
            val = float(raw_val)
        except (TypeError, ValueError):
            raise ValueError(
                f"waves[{i}].completion must be a number, got {raw_val!r}"
            )
        if not (0 <= val <= 100):
            raise ValueError(
                f"waves[{i}].completion={val} is outside the valid range [0, 100]"
            )
        waves.append(str(entry["wave"]))
        completion.append(val)

    return waves, completion


def build_wave_progress_figure():
    try:
        import plotly.graph_objects as go
    except ImportError as exc:
        raise SystemExit(
            'Plotly is required to generate wave progress. Install it with: pip install plotly'
        ) from exc

    waves, completion = load_wave_progression()

    fig = go.Figure()

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
