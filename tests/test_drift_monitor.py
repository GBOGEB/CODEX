import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DRIFT_MONITOR = ROOT / "telemetry" / "pca" / "drift_monitor.py"


def test_drift_monitor_bootstrap_banner():
    result = subprocess.run(
        [sys.executable, str(DRIFT_MONITOR)],
        capture_output=True,
        text=True,
        check=True,
    )

    assert "System initialized" in result.stdout


def test_drift_monitor_reports_drift_from_metric_files(tmp_path):
    baseline_path = tmp_path / "baseline.json"
    current_path = tmp_path / "current.json"

    baseline_path.write_text(
        json.dumps(
            {
                "structure": 0.8,
                "renderability": 0.7,
                "federation": 0.6,
                "semantic_traceability": 0.9,
                "orchestration_readiness": 0.5,
                "drift_stability": 0.4,
            }
        ),
        encoding="utf-8",
    )
    current_path.write_text(
        json.dumps(
            {
                "structure": 0.9,
                "renderability": 0.8,
                "federation": 0.55,
                "semantic_traceability": 0.95,
                "orchestration_readiness": 0.45,
                "drift_stability": 0.5,
            }
        ),
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(DRIFT_MONITOR),
            "--baseline",
            str(baseline_path),
            "--current",
            str(current_path),
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    report = json.loads(result.stdout)
    assert report["tracked_dimensions"] == [
        "structure",
        "renderability",
        "federation",
        "semantic_traceability",
        "orchestration_readiness",
        "drift_stability",
    ]
    assert report["drift_variance"] == 0.075
    assert report["deltas"]["structure"] == 0.1
    assert report["deltas"]["federation"] == -0.05
