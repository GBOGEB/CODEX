from __future__ import annotations

import json

import pytest

from telemetry.pca.drift_monitor import TRACKED_DIMENSIONS, calculate_drift_variance, main


def _metrics(value: float) -> dict[str, float]:
    return {metric: value for metric in TRACKED_DIMENSIONS}


def test_calculate_drift_variance_averages_complete_vectors() -> None:
    current_metrics = _metrics(0.75)
    baseline_metrics = _metrics(0.25)

    assert calculate_drift_variance(current_metrics, baseline_metrics) == pytest.approx(0.5)


def test_calculate_drift_variance_rejects_incomplete_vectors() -> None:
    current_metrics = _metrics(0.5)
    baseline_metrics = _metrics(0.5)
    baseline_metrics.pop("drift_stability")

    with pytest.raises(ValueError, match="baseline_metrics is missing required dimensions: drift_stability"):
        calculate_drift_variance(current_metrics, baseline_metrics)


def test_main_reports_initialization_payload(capsys: pytest.CaptureFixture[str]) -> None:
    assert main([]) == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "initialized"
    assert payload["version"] == "0.1.0"
    assert payload["tracked_dimensions"] == list(TRACKED_DIMENSIONS)


def test_main_reports_evaluated_variance(tmp_path, capsys: pytest.CaptureFixture[str]) -> None:
    current_path = tmp_path / "current.json"
    baseline_path = tmp_path / "baseline.json"
    current_path.write_text(json.dumps(_metrics(0.9)), encoding="utf-8")
    baseline_path.write_text(json.dumps(_metrics(0.4)), encoding="utf-8")

    assert main(["--current-file", str(current_path), "--baseline-file", str(baseline_path)]) == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "evaluated"
    assert payload["current_file"] == str(current_path)
    assert payload["baseline_file"] == str(baseline_path)
    assert payload["drift_variance"] == pytest.approx(0.5)
