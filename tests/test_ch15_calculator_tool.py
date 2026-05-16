from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.ch15_calculator_tool import (  # noqa: E402
    calculate_failure_rate,
    calculate_total_with_contingency,
    load_version,
)


def test_total_with_contingency():
    assert calculate_total_with_contingency(100.0, 10.0) == __import__("pytest").approx(110.0)


def test_failure_rate():
    assert calculate_failure_rate(5, 1000.0) == 0.005


def test_load_version_reads_repo_version_file():
    ver = load_version()
    assert ver.version
