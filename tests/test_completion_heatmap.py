"""Unit tests for visuals/completion_heatmap.py load_completion_metrics."""
import textwrap
from pathlib import Path

import pytest

from visuals.completion_heatmap import load_completion_metrics


def _write_manifest(tmp_path: Path, content: str) -> Path:
    p = tmp_path / 'PROGRAM_METRICS.yaml'
    p.write_text(textwrap.dedent(content), encoding='utf-8')
    return p


VALID_YAML = """\
    program_metrics:
      system: TEST
      metrics:
        governance:
          score: 86
        ci_cd:
          score: 62
        renderer:
          score: 74
          label: Renderer Engine
"""


class TestLoadCompletionMetricsValid:
    def test_correct_categories(self, tmp_path):
        manifest = _write_manifest(tmp_path, VALID_YAML)
        categories, _ = load_completion_metrics(manifest)
        assert categories == ['Governance', 'CI/CD', 'Renderer Engine']

    def test_ci_cd_label(self, tmp_path):
        manifest = _write_manifest(tmp_path, VALID_YAML)
        categories, _ = load_completion_metrics(manifest)
        assert 'CI/CD' in categories

    def test_returns_nested_list(self, tmp_path):
        manifest = _write_manifest(tmp_path, VALID_YAML)
        _, values = load_completion_metrics(manifest)
        # z should be a list of one row (for Plotly heatmap)
        assert len(values) == 1
        assert values[0] == [86.0, 62.0, 74.0]


class TestLoadCompletionMetricsErrors:
    def test_missing_file(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            load_completion_metrics(tmp_path / 'PROGRAM_METRICS.yaml')

    def test_invalid_schema(self, tmp_path):
        manifest = _write_manifest(tmp_path, '- list_item\n')
        with pytest.raises(ValueError):
            load_completion_metrics(manifest)

    def test_score_out_of_range(self, tmp_path):
        manifest = _write_manifest(
            tmp_path,
            'program_metrics:\n  metrics:\n    governance:\n      score: -10\n',
        )
        with pytest.raises(ValueError, match=r'\[0, 100\]'):
            load_completion_metrics(manifest)
