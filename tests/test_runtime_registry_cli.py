"""Subprocess regression tests for the federation runtime registry CLI."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE = "src.qplant_presentation_engine.runtime_registry"


def _invoke(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", MODULE, *arguments],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def test_cli_generates_registry_and_report_with_matching_counts(tmp_path: Path) -> None:
    registry_path = tmp_path / "generated" / "registry.json"
    report_path = tmp_path / "generated" / "report.json"

    result = _invoke(
        "--runtime-dir",
        str(ROOT / "federation" / "runtime_registry"),
        "--registry-output",
        str(registry_path),
        "--report-output",
        str(report_path),
    )

    assert result.returncode == 0, result.stderr
    summary = json.loads(result.stdout)
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    report = json.loads(report_path.read_text(encoding="utf-8"))

    assert summary["status"] == "generated"
    assert summary["runtime_status"] == "generated"
    assert summary["repo_count"] == 6
    assert summary["registry_output"] == str(registry_path)
    assert summary["report_output"] == str(report_path)
    assert registry["members"] == [
        "ABACUS", "ARTSTYLE", "QPLANT", "CODEX", "GEMINI", "ANTHROPIC"
    ]
    assert len(registry["runtime_registry"]) == summary["repo_count"]
    assert registry["wave"] == report["wave"]
    assert registry["subwave"] == report["subwave"]
    assert "federation_rollup" in report
    assert "federation_scree" in report
    assert len(report["truth_matrix"]["rows"]) == summary["repo_count"]


def test_cli_rejects_unsupported_legacy_overrides_without_writing(tmp_path: Path) -> None:
    for flag in ("--rollup-path", "--scree-path"):
        output_dir = tmp_path / flag.lstrip("-")
        registry_path = output_dir / "registry.json"
        report_path = output_dir / "report.json"
        result = _invoke(
            "--runtime-dir",
            str(ROOT / "federation" / "runtime_registry"),
            "--registry-output",
            str(registry_path),
            "--report-output",
            str(report_path),
            flag,
            str(tmp_path / "unsupported.json"),
        )
        assert result.returncode != 0
        assert "unsupported" in result.stderr.lower()
        assert not registry_path.exists()
        assert not report_path.exists()
