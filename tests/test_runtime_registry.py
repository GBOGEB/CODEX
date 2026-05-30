"""Tests for src/qplant_presentation_engine/runtime_registry.py."""
from __future__ import annotations

import json
from pathlib import Path

from src.qplant_presentation_engine.runtime_registry import (
    RUNTIME_FIELDS,
    RuntimeRegistry,
    generate_runtime_registry,
)


def _root() -> Path:
    return Path(__file__).resolve().parents[1]


def _runtime_dir() -> Path:
    return _root() / "federation" / "runtime_registry"


def _metrics_dir() -> Path:
    return _root() / "metrics" / "repo"


class TestRuntimeEvidenceFiles:
    def test_runtime_files_exist(self):
        runtime_dir = _runtime_dir()
        for name in ("abacus_runtime.json", "artstyle_runtime.json", "qplant_runtime.json", "codex_runtime.json"):
            assert (runtime_dir / name).exists()

    def test_runtime_files_have_required_fields(self):
        runtime_dir = _runtime_dir()
        for name in ("abacus_runtime.json", "artstyle_runtime.json", "qplant_runtime.json", "codex_runtime.json"):
            data = json.loads((runtime_dir / name).read_text(encoding="utf-8"))
            for field in RUNTIME_FIELDS:
                assert field in data, f"Missing field {field} in {name}"


class TestRuntimeRegistryGeneration:
    def test_write_outputs_generates_registry_and_report(self, tmp_path: Path):
        registry_output = tmp_path / "runtime_registry.json"
        report_output = tmp_path / "runtime_registry_report.json"
        registry, report = RuntimeRegistry().write_outputs(
            runtime_dir=_runtime_dir(),
            metrics_dir=_metrics_dir(),
            registry_output=registry_output,
            report_output=report_output,
        )
        assert registry_output.exists()
        assert report_output.exists()
        assert json.loads(registry_output.read_text(encoding="utf-8")) == registry
        assert json.loads(report_output.read_text(encoding="utf-8")) == report

    def test_registry_contains_all_members(self):
        registry, _ = RuntimeRegistry().write_outputs(
            runtime_dir=_runtime_dir(),
            metrics_dir=_metrics_dir(),
        )
        repos = {entry["repo"] for entry in registry["runtime_registry"]}
        assert repos == {
            "GBOGEB/ABACUS",
            "GBOGEB/ARTSTYLE",
            "GBOGEB/QPLANT",
            "GBOGEB/CODEX",
        }

    def test_report_integrates_rollup_scree_and_truth_matrix(self):
        _, report = RuntimeRegistry().write_outputs(
            runtime_dir=_runtime_dir(),
            metrics_dir=_metrics_dir(),
        )
        assert "federation_rollup" in report
        assert "federation_scree" in report
        assert "truth_matrix" in report
        assert "runtime_status" in report["federation_rollup"]
        assert "runtime_status" in report["federation_scree"]
        assert "rows" in report["truth_matrix"]

    def test_rollup_consumes_runtime_status_per_member(self):
        _, report = RuntimeRegistry().write_outputs(
            runtime_dir=_runtime_dir(),
            metrics_dir=_metrics_dir(),
        )
        runtime_status = report["federation_rollup"]["runtime_status"]["members"]
        assert set(runtime_status.keys()) == {"ABACUS", "ARTSTYLE", "QPLANT", "CODEX"}
        assert runtime_status["ABACUS"]["runtime_validated"] is True
        assert runtime_status["ARTSTYLE"]["runtime_validated"] is False

    def test_generate_runtime_registry_uses_defaults(self):
        registry, report = generate_runtime_registry(
            runtime_dir=_runtime_dir(),
            metrics_dir=_metrics_dir(),
        )
        assert registry["subwave"] == "W007.2"
        assert report["subwave"] == "W007.2"
