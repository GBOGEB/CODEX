"""Unit tests for visuals/program_metrics_manifest.py shared loader."""
import textwrap
from pathlib import Path

import pytest

from visuals.program_metrics_manifest import (
    load_program_metric_entries,
    metric_display_label,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

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
          status: active
        ci_cd:
          score: 62
          status: scaffolded
        renderer:
          score: 74
          label: Renderer Engine
"""


# ---------------------------------------------------------------------------
# metric_display_label
# ---------------------------------------------------------------------------

class TestMetricDisplayLabel:
    def test_explicit_label_used(self):
        assert metric_display_label('ci_cd', {'label': 'Custom CI/CD'}) == 'Custom CI/CD'

    def test_known_acronym_ci_cd(self):
        assert metric_display_label('ci_cd', {}) == 'CI/CD'

    def test_fallback_title(self):
        assert metric_display_label('renderer', {}) == 'Renderer'

    def test_multi_word_fallback(self):
        assert metric_display_label('publication_readiness', {}) == 'Publication Readiness'

    def test_explicit_label_overrides_acronym(self):
        assert metric_display_label('ci_cd', {'label': 'Pipeline'}) == 'Pipeline'


# ---------------------------------------------------------------------------
# load_program_metric_entries — valid manifest
# ---------------------------------------------------------------------------

class TestLoadProgramMetricEntriesValid:
    def test_returns_correct_number_of_entries(self, tmp_path):
        manifest = _write_manifest(tmp_path, VALID_YAML)
        entries = load_program_metric_entries(manifest)
        assert len(entries) == 3

    def test_returns_correct_names(self, tmp_path):
        manifest = _write_manifest(tmp_path, VALID_YAML)
        names = [name for name, _ in load_program_metric_entries(manifest)]
        assert names == ['governance', 'ci_cd', 'renderer']

    def test_returns_correct_scores(self, tmp_path):
        manifest = _write_manifest(tmp_path, VALID_YAML)
        scores = [data['score'] for _, data in load_program_metric_entries(manifest)]
        assert scores == [86, 62, 74]

    def test_explicit_label_preserved(self, tmp_path):
        manifest = _write_manifest(tmp_path, VALID_YAML)
        entries = dict(load_program_metric_entries(manifest))
        assert entries['renderer']['label'] == 'Renderer Engine'


# ---------------------------------------------------------------------------
# load_program_metric_entries — missing file
# ---------------------------------------------------------------------------

class TestLoadProgramMetricEntriesMissingFile:
    def test_raises_file_not_found(self, tmp_path):
        with pytest.raises(FileNotFoundError, match='PROGRAM_METRICS.yaml'):
            load_program_metric_entries(tmp_path / 'PROGRAM_METRICS.yaml')


# ---------------------------------------------------------------------------
# load_program_metric_entries — malformed schema
# ---------------------------------------------------------------------------

class TestLoadProgramMetricEntriesMalformed:
    def test_non_dict_root(self, tmp_path):
        manifest = _write_manifest(tmp_path, '- item\n')
        with pytest.raises(ValueError, match='expected top-level mapping'):
            load_program_metric_entries(manifest)

    def test_missing_program_metrics_key(self, tmp_path):
        manifest = _write_manifest(tmp_path, 'other: value\n')
        with pytest.raises(ValueError, match='"program_metrics"'):
            load_program_metric_entries(manifest)

    def test_empty_metrics_dict(self, tmp_path):
        manifest = _write_manifest(tmp_path, 'program_metrics:\n  metrics: {}\n')
        with pytest.raises(ValueError, match='non-empty'):
            load_program_metric_entries(manifest)

    def test_metric_entry_not_dict(self, tmp_path):
        manifest = _write_manifest(
            tmp_path,
            'program_metrics:\n  metrics:\n    governance: not_a_dict\n',
        )
        with pytest.raises(ValueError, match='governance'):
            load_program_metric_entries(manifest)

    def test_score_not_number(self, tmp_path):
        manifest = _write_manifest(
            tmp_path,
            'program_metrics:\n  metrics:\n    governance:\n      score: "high"\n',
        )
        with pytest.raises(ValueError, match='governance.score'):
            load_program_metric_entries(manifest)

    def test_score_above_100(self, tmp_path):
        manifest = _write_manifest(
            tmp_path,
            'program_metrics:\n  metrics:\n    governance:\n      score: 150\n',
        )
        with pytest.raises(ValueError, match=r'\[0, 100\]'):
            load_program_metric_entries(manifest)

    def test_score_below_0(self, tmp_path):
        manifest = _write_manifest(
            tmp_path,
            'program_metrics:\n  metrics:\n    governance:\n      score: -5\n',
        )
        with pytest.raises(ValueError, match=r'\[0, 100\]'):
            load_program_metric_entries(manifest)
