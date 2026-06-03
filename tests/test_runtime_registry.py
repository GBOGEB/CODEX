"""Tests for src/qplant_presentation_engine/runtime_registry.py."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.qplant_presentation_engine.runtime_registry import (
    FEDERATION_MEMBERS,
    RUNTIME_FIELDS,
    RuntimeRegistry,
    RuntimeRegistryError,
    generate_runtime_registry,
)


def _root() -> Path:
    return Path(__file__).resolve().parents[1]


def _runtime_dir() -> Path:
    return _root() / "federation" / "runtime_registry"


def _metrics_dir() -> Path:
    return _root() / "metrics" / "repo"


def _copy_metrics_inputs(destination: Path) -> Path:
    source = _metrics_dir()
    destination.mkdir(parents=True, exist_ok=True)
    for name in (
        "abacus_metrics.json",
        "artstyle_metrics.json",
        "qplant_metrics.json",
        "codex_metrics.json",
        "gemini_metrics.json",
        "anthropic_metrics.json",
    ):
        (destination / name).write_text((source / name).read_text(encoding="utf-8"), encoding="utf-8")
    return destination


def _copy_runtime_inputs(destination: Path) -> Path:
    source = _runtime_dir()
    destination.mkdir(parents=True, exist_ok=True)
    for name in (
        "abacus_runtime.json",
        "artstyle_runtime.json",
        "qplant_runtime.json",
        "codex_runtime.json",
        "gemini_runtime.json",
        "anthropic_runtime.json",
    ):
        (destination / name).write_text((source / name).read_text(encoding="utf-8"), encoding="utf-8")
    return destination


class TestRuntimeEvidenceFiles:
    def test_runtime_files_exist(self):
        runtime_dir = _runtime_dir()
        for name in (
            "abacus_runtime.json",
            "artstyle_runtime.json",
            "qplant_runtime.json",
            "codex_runtime.json",
            "gemini_runtime.json",
            "anthropic_runtime.json",
        ):
            assert (runtime_dir / name).exists()

    def test_runtime_files_have_required_fields(self):
        runtime_dir = _runtime_dir()
        for name in (
            "abacus_runtime.json",
            "artstyle_runtime.json",
            "qplant_runtime.json",
            "codex_runtime.json",
            "gemini_runtime.json",
            "anthropic_runtime.json",
        ):
            data = json.loads((runtime_dir / name).read_text(encoding="utf-8"))
            for field in RUNTIME_FIELDS:
                assert field in data, f"Missing field {field} in {name}"


class TestRuntimeRegistryGeneration:
    def test_write_outputs_generates_registry_and_report(self, tmp_path: Path):
        runtime_dir = _copy_runtime_inputs(tmp_path / "runtime_registry")
        registry_output = tmp_path / "runtime_registry.json"
        report_output = tmp_path / "runtime_registry_report.json"
        registry, report = RuntimeRegistry().write_outputs(
            runtime_dir=runtime_dir,
            metrics_dir=_metrics_dir(),
            registry_output=registry_output,
            report_output=report_output,
        )
        assert registry_output.exists()
        assert report_output.exists()
        assert json.loads(registry_output.read_text(encoding="utf-8")) == registry
        assert json.loads(report_output.read_text(encoding="utf-8")) == report

    def test_registry_contains_all_members(self, tmp_path: Path):
        runtime_dir = _copy_runtime_inputs(tmp_path / "runtime_registry")
        registry_output = tmp_path / "runtime_registry.json"
        report_output = tmp_path / "runtime_registry_report.json"
        registry, _ = RuntimeRegistry().write_outputs(
            runtime_dir=runtime_dir,
            metrics_dir=_metrics_dir(),
            registry_output=registry_output,
            report_output=report_output,
        )
        repos = {entry["repo"] for entry in registry["runtime_registry"]}
        assert repos == {f"GBOGEB/{member}" for member in FEDERATION_MEMBERS}

    def test_report_integrates_rollup_scree_and_truth_matrix(self, tmp_path: Path):
        runtime_dir = _copy_runtime_inputs(tmp_path / "runtime_registry")
        registry_output = tmp_path / "runtime_registry.json"
        report_output = tmp_path / "runtime_registry_report.json"
        _, report = RuntimeRegistry().write_outputs(
            runtime_dir=runtime_dir,
            metrics_dir=_metrics_dir(),
            registry_output=registry_output,
            report_output=report_output,
        )
        assert "federation_rollup" in report
        assert "federation_scree" in report
        assert "truth_matrix" in report
        assert "runtime_status" in report["federation_rollup"]
        assert "runtime_status" in report["federation_scree"]
        assert "rows" in report["truth_matrix"]

    def test_rollup_consumes_runtime_status_per_member(self, tmp_path: Path):
        runtime_dir = _copy_runtime_inputs(tmp_path / "runtime_registry")
        registry_output = tmp_path / "runtime_registry.json"
        report_output = tmp_path / "runtime_registry_report.json"
        _, report = RuntimeRegistry().write_outputs(
            runtime_dir=runtime_dir,
            metrics_dir=_metrics_dir(),
            registry_output=registry_output,
            report_output=report_output,
        )
        runtime_status = report["federation_rollup"]["runtime_status"]["members"]
        assert set(runtime_status.keys()) == set(FEDERATION_MEMBERS)
        assert runtime_status["ABACUS"]["runtime_validated"] is True
        assert runtime_status["ARTSTYLE"]["runtime_validated"] is False

    def test_generate_runtime_registry_uses_defaults(self, tmp_path: Path):
        runtime_dir = _copy_runtime_inputs(tmp_path / "runtime_registry")
        registry, report = generate_runtime_registry(
            runtime_dir=runtime_dir,
            metrics_dir=_metrics_dir(),
        )
        assert registry["subwave"] == "W007.2A"
        assert report["subwave"] == "W007.2A"
        assert (runtime_dir / "runtime_registry.json").exists()
        assert (runtime_dir / "runtime_registry_report.json").exists()

    def test_write_outputs_normalizes_member_order(self, tmp_path: Path):
        runtime_dir = _copy_runtime_inputs(tmp_path / "runtime_registry")
        registry_output = tmp_path / "runtime_registry.json"
        report_output = tmp_path / "runtime_registry_report.json"

        registry, report = RuntimeRegistry(
            members=("ANTHROPIC", "GEMINI", "CODEX", "QPLANT", "ABACUS", "ARTSTYLE")
        ).write_outputs(
            runtime_dir=runtime_dir,
            metrics_dir=_metrics_dir(),
            registry_output=registry_output,
            report_output=report_output,
        )

        assert registry["members"] == list(FEDERATION_MEMBERS)
        assert [row["member"] for row in report["truth_matrix"]["rows"]] == list(FEDERATION_MEMBERS)
        assert list(report["federation_rollup"]["runtime_status"]["members"].keys()) == list(FEDERATION_MEMBERS)

    def test_runtime_report_rejects_non_canonical_member_set(self, tmp_path: Path):
        runtime_dir = _copy_runtime_inputs(tmp_path / "runtime_registry")
        entries = RuntimeRegistry().load_runtime_entries(runtime_dir)
        repo_metrics = RuntimeRegistry()._load_repo_metrics(_metrics_dir())

        with pytest.raises(RuntimeRegistryError, match="canonical federation members"):
            RuntimeRegistry().build_runtime_report(
                entries,
                repo_metrics,
                members=("ABACUS", "QPLANT"),
            )

    def test_rejects_invalid_runtime_field_types(self, tmp_path: Path):
        runtime_dir = _copy_runtime_inputs(tmp_path / "runtime_registry")
        abacus_file = runtime_dir / "abacus_runtime.json"
        data = json.loads(abacus_file.read_text(encoding="utf-8"))
        data["runtime_exists"] = "false"
        abacus_file.write_text(json.dumps(data), encoding="utf-8")

        with pytest.raises(RuntimeRegistryError, match="runtime_exists"):
            RuntimeRegistry().load_runtime_entries(runtime_dir)

    def test_load_runtime_entries_rejects_malformed_json(self, tmp_path: Path):
        runtime_dir = _copy_runtime_inputs(tmp_path / "runtime_registry")
        (runtime_dir / "abacus_runtime.json").write_text("{", encoding="utf-8")

        with pytest.raises(RuntimeRegistryError, match="Invalid runtime evidence JSON for ABACUS"):
            RuntimeRegistry().load_runtime_entries(runtime_dir)

    def test_load_runtime_entries_rejects_non_object_payload(self, tmp_path: Path):
        runtime_dir = _copy_runtime_inputs(tmp_path / "runtime_registry")
        (runtime_dir / "abacus_runtime.json").write_text("[]", encoding="utf-8")

        with pytest.raises(RuntimeRegistryError, match="expected JSON object"):
            RuntimeRegistry().load_runtime_entries(runtime_dir)

    def test_custom_unknown_member_raises_runtime_registry_error(self, tmp_path: Path):
        runtime_dir = _copy_runtime_inputs(tmp_path / "runtime_registry")
        with pytest.raises(RuntimeRegistryError, match="filename configured"):
            RuntimeRegistry(members=("ABACUS", "UNKNOWN")).load_runtime_entries(runtime_dir)

    def test_runtime_status_handles_empty_members(self):
        status = RuntimeRegistry(members=())._runtime_status({})
        assert status["members"] == {}
        assert status["coverage"]["runtime_exists"] == 0.0
        assert status["coverage"]["runtime_validated"] == 0.0
        assert status["coverage"]["deployment_exists"] == 0.0
        assert status["coverage"]["truth_score_average"] == 0.0

    def test_rejects_duplicate_members(self, tmp_path: Path):
        runtime_dir = _copy_runtime_inputs(tmp_path / "runtime_registry")
        registry_output = tmp_path / "runtime_registry.json"
        report_output = tmp_path / "runtime_registry_report.json"
        with pytest.raises(RuntimeRegistryError, match="canonical federation members"):
            RuntimeRegistry(members=("ABACUS", "ABACUS", "ARTSTYLE", "QPLANT", "CODEX", "GEMINI")).write_outputs(
                runtime_dir=runtime_dir,
                metrics_dir=_metrics_dir(),
                registry_output=registry_output,
                report_output=report_output,
            )

    def test_rejects_bool_in_numeric_fields(self, tmp_path: Path):
        runtime_dir = _copy_runtime_inputs(tmp_path / "runtime_registry")
        abacus_file = runtime_dir / "abacus_runtime.json"
        data = json.loads(abacus_file.read_text(encoding="utf-8"))
        data["truth_score"] = True
        abacus_file.write_text(json.dumps(data), encoding="utf-8")

        with pytest.raises(RuntimeRegistryError, match="truth_score.*expected number"):
            RuntimeRegistry().load_runtime_entries(runtime_dir)

    def test_rejects_out_of_range_pca_variance(self, tmp_path: Path):
        runtime_dir = _copy_runtime_inputs(tmp_path / "runtime_registry")
        abacus_file = runtime_dir / "abacus_runtime.json"
        data = json.loads(abacus_file.read_text(encoding="utf-8"))
        data["forward_pca"]["variance_explained"] = [1.5, 0.2, 0.1, 0.1, 0.1]
        abacus_file.write_text(json.dumps(data), encoding="utf-8")

        with pytest.raises(RuntimeRegistryError, match="variance_explained.*expected value in"):
            RuntimeRegistry().load_runtime_entries(runtime_dir)

    def test_rejects_out_of_range_pca_score(self, tmp_path: Path):
        runtime_dir = _copy_runtime_inputs(tmp_path / "runtime_registry")
        abacus_file = runtime_dir / "abacus_runtime.json"
        data = json.loads(abacus_file.read_text(encoding="utf-8"))
        data["forward_pca"]["convergence_score"] = 1.5
        abacus_file.write_text(json.dumps(data), encoding="utf-8")

        with pytest.raises(RuntimeRegistryError, match="convergence_score.*expected value in"):
            RuntimeRegistry().load_runtime_entries(runtime_dir)

    def test_load_repo_metrics_rejects_malformed_json(self, tmp_path: Path):
        metrics_dir = _copy_metrics_inputs(tmp_path / "metrics")
        (metrics_dir / "abacus_metrics.json").write_text("{", encoding="utf-8")

        with pytest.raises(RuntimeRegistryError, match="Invalid repository metrics JSON for ABACUS"):
            RuntimeRegistry()._load_repo_metrics(metrics_dir)

    def test_load_repo_metrics_rejects_non_object_payload(self, tmp_path: Path):
        metrics_dir = _copy_metrics_inputs(tmp_path / "metrics")
        (metrics_dir / "abacus_metrics.json").write_text("[]", encoding="utf-8")

        with pytest.raises(RuntimeRegistryError, match="expected JSON object"):
            RuntimeRegistry()._load_repo_metrics(metrics_dir)

    def test_write_outputs_json_sorted_keys(self, tmp_path: Path):
        runtime_dir = _copy_runtime_inputs(tmp_path / "runtime_registry")
        metrics_dir = _copy_metrics_inputs(tmp_path / "metrics")
        registry_output = tmp_path / "registry.json"
        report_output = tmp_path / "report.json"

        RuntimeRegistry().write_outputs(
            runtime_dir=runtime_dir,
            metrics_dir=metrics_dir,
            registry_output=registry_output,
            report_output=report_output,
        )

        for path in [registry_output, report_output]:
            raw = path.read_text(encoding="utf-8")
            parsed = json.loads(raw)
            assert raw == json.dumps(parsed, indent=2, sort_keys=True)
