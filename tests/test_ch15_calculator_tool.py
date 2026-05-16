import json
from pathlib import Path

import pytest

from src.ch15_calculator_tool import (
    build_sample_stats,
    calculate_failure_rate,
    calculate_total_with_contingency,
    load_input_sample,
    load_version,
)


def test_total_with_contingency():
    assert calculate_total_with_contingency(100.0, 10.0) == pytest.approx(110.0)


def test_total_with_contingency_rejects_negative_inputs():
    with pytest.raises(ValueError, match="base_cost"):
        calculate_total_with_contingency(-1.0, 10.0)
    with pytest.raises(ValueError, match="contingency_pct"):
        calculate_total_with_contingency(100.0, -1.0)


def test_failure_rate():
    assert calculate_failure_rate(5, 1000.0) == pytest.approx(0.005)


def test_failure_rate_rejects_invalid_inputs():
    with pytest.raises(ValueError, match="failures"):
        calculate_failure_rate(-1, 1.0)
    with pytest.raises(ValueError, match="operating_hours"):
        calculate_failure_rate(1, 0)


def test_load_version_reads_repo_version_file():
    ver = load_version()
    assert ver.version


def test_load_version_requires_non_empty_version(tmp_path: Path):
    bad_version_file = tmp_path / "VERSION.json"
    bad_version_file.write_text(json.dumps({"version": ""}), encoding="utf-8")

    with pytest.raises(ValueError, match="non-empty"):
        load_version(bad_version_file)


def test_load_input_sample_and_build_stats():
    sample = load_input_sample("inputs/ch15/sample_input_v1.json")
    stats = build_sample_stats(sample)
    assert stats["total_with_contingency"] == pytest.approx(140625.0)
    assert stats["failure_rate_per_hour"] == pytest.approx(3 / 8760.0)


def test_load_input_sample_requires_fields(tmp_path: Path):
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps({"base_cost": 1}), encoding="utf-8")
    with pytest.raises(ValueError, match="Missing required fields"):
        load_input_sample(bad)
