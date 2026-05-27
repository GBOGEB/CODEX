from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.check_bridge_health import main as check_bridge_health_main
from src.bridge_adapter import build_bridge_report, bridge_alignment_matrix

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_build_bridge_report_passes_for_all_components() -> None:
    for component in ("codex", "abacus", "mcp-bridge"):
        report = build_bridge_report(REPO_ROOT, component)
        assert report["status"] == "pass"
        assert report["issues"] == []
        assert report["component"] == component


def test_build_bridge_report_rejects_unknown_component() -> None:
    with pytest.raises(ValueError, match="Unknown component 'unknown'"):
        build_bridge_report(REPO_ROOT, "unknown")


def test_bridge_alignment_matrix_covers_runtime_manifest_modules() -> None:
    report = build_bridge_report(REPO_ROOT, "mcp-bridge")
    alignment = bridge_alignment_matrix()

    assert set(report["runtime"]["modules"]).issubset(alignment)
    assert report["alignment"]["telemetry"] == [
        "telemetry/pca/drift_monitor.py",
        "dashboards/telemetry_dashboard.py",
    ]


def test_check_bridge_health_writes_json_report(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    report_path = tmp_path / "bridge-report.json"

    assert check_bridge_health_main(["--component", "mcp-bridge", "--report", str(report_path)]) == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "pass"
    assert json.loads(report_path.read_text(encoding="utf-8")) == payload
