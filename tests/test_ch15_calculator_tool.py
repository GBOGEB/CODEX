from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.ch15_calculator_tool import (  # noqa: E402
    calculate_failure_rate,
    calculate_total_with_contingency,
    load_version,
)


def test_total_with_contingency():
    assert calculate_total_with_contingency(100.0, 10.0) == pytest.approx(110.0)


def test_failure_rate():
    assert calculate_failure_rate(5, 1000.0) == 0.005


def test_load_version_reads_version_file(tmp_path):
    version_file = tmp_path / "VERSION.json"
    version_file.write_text(
        '{"version":"9.9.9","git":"abc1234","generated_at":"2026-01-01T00:00:00Z"}',
        encoding="utf-8",
    )

    ver = load_version(version_file=version_file)

    assert ver.version == "9.9.9"
    assert ver.git == "abc1234"
    assert ver.generated_at == "2026-01-01T00:00:00Z"
