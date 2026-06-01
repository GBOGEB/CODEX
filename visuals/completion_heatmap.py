from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

_DEFAULT_MANIFEST = Path(__file__).resolve().parents[1] / "MANIFEST" / "PROGRAM_METRICS.yaml"

# Map of YAML metric keys to their display labels.  Keys not listed here are
# converted by replacing underscores with spaces and title-casing each word.
_KEY_LABELS: dict[str, str] = {
    "ci_cd": "CI/CD",
}


def _default_label(key: str) -> str:
    return _KEY_LABELS.get(key, key.replace("_", " ").title())


def load_completion_metrics(
    path: Path | None = None,
) -> tuple[list[str], list[list[float]]]:
    """Load completion metrics from a ``PROGRAM_METRICS.yaml`` manifest.

    Args:
        path: Path to the manifest file.  Defaults to
            ``MANIFEST/PROGRAM_METRICS.yaml`` relative to the repo root.

    Returns:
        A ``(categories, values)`` tuple where *categories* is a list of
        display labels and *values* is a ``[[float, ...]]`` list suitable for
        a Plotly heatmap ``z`` parameter.

    Raises:
        FileNotFoundError: If *path* does not exist.
        ValueError: If the manifest schema is invalid or a score is out of
            the valid range ``[0, 100]``.
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

    program_metrics = raw.get("program_metrics", {})
    if not isinstance(program_metrics, dict):
        raise ValueError('"program_metrics" must be a mapping')

    metrics: Any = program_metrics.get("metrics")
    if not isinstance(metrics, dict):
        raise ValueError('"program_metrics.metrics" must be a mapping')

    categories: list[str] = []
    row: list[float] = []

    for key, spec in metrics.items():
        if not isinstance(spec, dict):
            raise ValueError(f'metrics.{key} must be a mapping')

        label = spec.get("label") or _default_label(key)
        raw_score = spec.get("score")
        try:
            score = float(raw_score)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            raise ValueError(
                f'metrics.{key}.score must be a number, got {raw_score!r}'
            )
        if not (0 <= score <= 100):
            raise ValueError(
                f'metrics.{key}.score={score} is outside the valid range [0, 100]'
            )
        categories.append(label)
        row.append(score)

    return categories, [row]


categories = [
    'Governance',
    'Rendering',
    'Validation',
    'Orchestration',
    'Thermodynamics',
    'Publication',
]

status_values = [[95, 82, 61, 73, 38, 57]]


def build_completion_heatmap():
    try:
        import plotly.graph_objects as go
    except ImportError as exc:
        raise SystemExit(
            'Plotly is required to generate completion heatmap. Install it with: pip install plotly'
        ) from exc

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
