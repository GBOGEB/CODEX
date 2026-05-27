"""Shared loader for MANIFEST/PROGRAM_METRICS.yaml.

All visualization scripts that read program-maturity scores should
import ``load_program_metric_entries`` from this module so that schema
validation and display-label logic stay in a single place.
"""

from pathlib import Path

# Known acronyms that .title() renders incorrectly (e.g. ci_cd -> 'Ci Cd').
# Add additional entries here as new metric keys are introduced.
_ACRONYM_LABELS: dict[str, str] = {
    'ci_cd': 'CI/CD',
}


def metric_display_label(metric_name: str, metric_data: dict) -> str:
    """Return a human-readable display label for a metric entry.

    Priority:
    1. Explicit ``label`` field in the manifest entry.
    2. Known acronym mapping (e.g. ``ci_cd`` → ``CI/CD``).
    3. Fallback: ``metric_name.replace('_', ' ').title()``.
    """
    if isinstance(metric_data, dict):
        explicit = metric_data.get('label')
        if isinstance(explicit, str) and explicit.strip():
            return explicit.strip()
    if metric_name in _ACRONYM_LABELS:
        return _ACRONYM_LABELS[metric_name]
    return metric_name.replace('_', ' ').title()


def load_program_metric_entries(manifest_path: Path) -> list[tuple[str, dict]]:
    """Load and validate metric entries from ``MANIFEST/PROGRAM_METRICS.yaml``.

    Returns a list of ``(metric_name, metric_data)`` tuples in manifest order.
    Each ``metric_data`` dict is guaranteed to contain a ``score`` that is a
    float in [0, 100].

    Raises:
        FileNotFoundError: if the manifest file does not exist.
        ValueError: if the manifest schema is invalid or a score is out of range.
        ImportError: if PyYAML is not installed.
    """
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
            "Expected MANIFEST/PROGRAM_METRICS.yaml in repository root."
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

    entries: list[tuple[str, dict]] = []
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
        if not (0 <= float(score) <= 100):
            raise ValueError(
                f'Invalid program metrics manifest schema at metrics.{metric_name}.score: '
                f'expected value in [0, 100], got {score}.'
            )
        entries.append((metric_name, metric_data))

    return entries
