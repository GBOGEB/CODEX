"""Unit tests for visuals/maturity_radar.py load_program_metrics."""
import textwrap
from pathlib import Path

import pytest

from visuals.maturity_radar import load_program_metrics


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


class TestLoadProgramMetricsValid:
    def test_correct_categories(self, tmp_path):
        manifest = _write_manifest(tmp_path, VALID_YAML)
        categories, _ = load_program_metrics(manifest)
        assert categories == ['Governance', 'CI/CD', 'Renderer Engine']

    def test_ci_cd_label(self, tmp_path):
        manifest = _write_manifest(tmp_path, VALID_YAML)
        categories, _ = load_program_metrics(manifest)
        assert 'CI/CD' in categories

    def test_explicit_label_used(self, tmp_path):
        manifest = _write_manifest(tmp_path, VALID_YAML)
        categories, _ = load_program_metrics(manifest)
        assert 'Renderer Engine' in categories

    def test_correct_scores(self, tmp_path):
        manifest = _write_manifest(tmp_path, VALID_YAML)
        _, values = load_program_metrics(manifest)
        assert values == [86.0, 62.0, 74.0]


class TestLoadProgramMetricsErrors:
    def test_missing_file(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            load_program_metrics(tmp_path / 'PROGRAM_METRICS.yaml')

    def test_invalid_schema(self, tmp_path):
        manifest = _write_manifest(tmp_path, '- list_item\n')
        with pytest.raises(ValueError):
            load_program_metrics(manifest)

    def test_score_out_of_range(self, tmp_path):
        manifest = _write_manifest(
            tmp_path,
            'program_metrics:\n  metrics:\n    governance:\n      score: 200\n',
        )
        with pytest.raises(ValueError, match=r'\[0, 100\]'):
            load_program_metrics(manifest)
