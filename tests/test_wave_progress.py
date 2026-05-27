"""Unit tests for visuals/wave_progress.py load_wave_progression."""
import textwrap
from pathlib import Path

import pytest

from visuals.wave_progress import load_wave_progression


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_manifest(tmp_path: Path, content: str) -> Path:
    p = tmp_path / 'WAVE_PROGRESSION.yaml'
    p.write_text(textwrap.dedent(content), encoding='utf-8')
    return p


VALID_YAML = """\
    waves:
      - wave: A1
        focus: initial_extraction
        completion: 100
      - wave: A6
        focus: governance
        completion: 86
      - wave: A7
        focus: telemetry
        completion: 41
"""


# ---------------------------------------------------------------------------
# Valid manifest
# ---------------------------------------------------------------------------

class TestLoadWaveProgressionValid:
    def test_returns_correct_waves(self, tmp_path):
        manifest = _write_manifest(tmp_path, VALID_YAML)
        waves, completion = load_wave_progression(manifest)
        assert waves == ['A1', 'A6', 'A7']

    def test_returns_correct_completion(self, tmp_path):
        manifest = _write_manifest(tmp_path, VALID_YAML)
        waves, completion = load_wave_progression(manifest)
        assert completion == [100.0, 86.0, 41.0]

    def test_boundary_zero(self, tmp_path):
        content = 'waves:\n  - wave: A0\n    completion: 0\n'
        manifest = _write_manifest(tmp_path, content)
        _, completion = load_wave_progression(manifest)
        assert completion == [0.0]

    def test_boundary_hundred(self, tmp_path):
        content = 'waves:\n  - wave: A1\n    completion: 100\n'
        manifest = _write_manifest(tmp_path, content)
        _, completion = load_wave_progression(manifest)
        assert completion == [100.0]


# ---------------------------------------------------------------------------
# Missing file
# ---------------------------------------------------------------------------

class TestLoadWaveProgressionMissingFile:
    def test_raises_file_not_found(self, tmp_path):
        with pytest.raises(FileNotFoundError, match='WAVE_PROGRESSION.yaml'):
            load_wave_progression(tmp_path / 'WAVE_PROGRESSION.yaml')


# ---------------------------------------------------------------------------
# Malformed schema
# ---------------------------------------------------------------------------

class TestLoadWaveProgressionMalformed:
    def test_non_dict_root(self, tmp_path):
        manifest = _write_manifest(tmp_path, '- A1\n- A2\n')
        with pytest.raises(ValueError, match='mapping'):
            load_wave_progression(manifest)

    def test_waves_not_list(self, tmp_path):
        manifest = _write_manifest(tmp_path, 'waves: not_a_list\n')
        with pytest.raises(ValueError, match='"waves"'):
            load_wave_progression(manifest)

    def test_entry_not_dict(self, tmp_path):
        manifest = _write_manifest(tmp_path, 'waves:\n  - just_a_string\n')
        with pytest.raises(ValueError, match=r'waves\[0\]'):
            load_wave_progression(manifest)

    def test_missing_wave_key(self, tmp_path):
        manifest = _write_manifest(tmp_path, 'waves:\n  - completion: 50\n')
        with pytest.raises(ValueError, match=r'waves\[0\]'):
            load_wave_progression(manifest)

    def test_missing_completion_key(self, tmp_path):
        manifest = _write_manifest(tmp_path, 'waves:\n  - wave: A1\n')
        with pytest.raises(ValueError, match=r'waves\[0\]'):
            load_wave_progression(manifest)

    def test_completion_not_number(self, tmp_path):
        manifest = _write_manifest(tmp_path, 'waves:\n  - wave: A1\n    completion: done\n')
        with pytest.raises(ValueError, match=r'waves\[0\].completion'):
            load_wave_progression(manifest)

    def test_completion_above_100(self, tmp_path):
        manifest = _write_manifest(tmp_path, 'waves:\n  - wave: A1\n    completion: 101\n')
        with pytest.raises(ValueError, match=r'\[0, 100\]'):
            load_wave_progression(manifest)

    def test_completion_below_0(self, tmp_path):
        manifest = _write_manifest(tmp_path, 'waves:\n  - wave: A1\n    completion: -1\n')
        with pytest.raises(ValueError, match=r'\[0, 100\]'):
            load_wave_progression(manifest)
