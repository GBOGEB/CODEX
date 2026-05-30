"""Tests for src/qplant_presentation_engine/runtime_registry.py."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.qplant_presentation_engine.federation_rollup import FederationRollup
from src.qplant_presentation_engine.federation_scree import FederationScree
from src.qplant_presentation_engine.runtime_registry import (
    DEFAULT_REPORT_OUTPUT,
    DEFAULT_REGISTRY_OUTPUT,
    DEFAULT_RUNTIME_DIR,
    MEMBERS,
    REQUIRED_FIELDS,
    RuntimeRegistry,
    RuntimeRegistryError,
)


ROOT = Path(__file__).resolve().parents[1]


def _runtime_records() -> dict[str, dict[str, object]]:
    return {
        "ABACUS": {
            "repo": "GBOGEB/ABACUS",
            "runtime_exists": True,
            "runtime_validated": True,
            "deployment_exists": True,
            "last_execution": "2026-05-30T09:00:00Z",
            "last_validation": "2026-05-30T10:00:00Z",
            "last_deployment": "2026-05-30T11:00:00Z",
            "truth_score": 1.0,
            "forward_pca": 0.84,
            "backward_pca": 0.81,
            "geti": 0.82,
            "pci": 0.79,
        },
        "ARTSTYLE": {
            "repo": "GBOGEB/ARTSTYLE",
            "runtime_exists": True,
            "runtime_validated": False,
            "deployment_exists": False,
            "last_execution": "2026-05-29T14:00:00Z",
            "last_validation": None,
            "last_deployment": None,
            "truth_score": 0.333333,
            "forward_pca": 0.73,
            "backward_pca": 0.70,
            "geti": 0.71,
            "pci": 0.68,
        },
        "QPLANT": {
            "repo": "GBOGEB/QPLANT",
            "runtime_exists": True,
            "runtime_validated": True,
            "deployment_exists": False,
            "last_execution": "2026-05-30T08:30:00Z",
            "last_validation": "2026-05-30T09:45:00Z",
            "last_deployment": None,
            "truth_score": 0.666667,
            "forward_pca": 0.79,
            "backward_pca": 0.75,
            "geti": 0.77,
            "pci": 0.74,
        },
        "CODEX": {
            "repo": "GBOGEB/CODEX",
            "runtime_exists": True,
            "runtime_validated": True,
            "deployment_exists": True,
            "last_execution": "2026-05-30T12:00:00Z",
            "last_validation": "2026-05-30T12:30:00Z",
            "last_deployment": "2026-05-30T13:00:00Z",
            "truth_score": 1.0,
            "forward_pca": 0.87,
            "backward_pca": 0.84,
            "geti": 0.85,
            "pci": 0.83,
        },
    }


def _repo_metrics() -> dict[str, dict[str, object]]:
    return {
        "ABACUS": {"metrics": {"forward_pca": {"variance_explained": [0.42, 0.26, 0.17, 0.10, 0.05], "convergence_score": 0.84}, "backward_pca": {"variance_explained": [0.40, 0.27, 0.18, 0.10, 0.05], "regression_score": 0.81}, "geti": 0.82, "pci": 0.79, "expansion_factor": 1.18, "scree": {"pc1": 0.42, "pc2": 0.26, "pc3": 0.17, "pc4": 0.10, "pc5": 0.05}}},
        "ARTSTYLE": {"metrics": {"forward_pca": {"variance_explained": [0.38, 0.28, 0.19, 0.10, 0.05], "convergence_score": 0.73}, "backward_pca": {"variance_explained": [0.36, 0.29, 0.20, 0.10, 0.05], "regression_score": 0.70}, "geti": 0.71, "pci": 0.68, "expansion_factor": 1.22, "scree": {"pc1": 0.38, "pc2": 0.28, "pc3": 0.19, "pc4": 0.10, "pc5": 0.05}}},
        "QPLANT": {"metrics": {"forward_pca": {"variance_explained": [0.44, 0.24, 0.18, 0.09, 0.05], "convergence_score": 0.79}, "backward_pca": {"variance_explained": [0.41, 0.25, 0.20, 0.09, 0.05], "regression_score": 0.75}, "geti": 0.77, "pci": 0.74, "expansion_factor": 1.15, "scree": {"pc1": 0.44, "pc2": 0.24, "pc3": 0.18, "pc4": 0.09, "pc5": 0.05}}},
        "CODEX": {"metrics": {"forward_pca": {"variance_explained": [0.40, 0.27, 0.18, 0.10, 0.05], "convergence_score": 0.87}, "backward_pca": {"variance_explained": [0.38, 0.28, 0.19, 0.10, 0.05], "regression_score": 0.84}, "geti": 0.85, "pci": 0.83, "expansion_factor": 1.12, "scree": {"pc1": 0.40, "pc2": 0.27, "pc3": 0.18, "pc4": 0.10, "pc5": 0.05}}},
    }


class TestRuntimeRegistryValidation:
    def test_default_weights_cover_all_members(self):
        registry = RuntimeRegistry()
        assert set(registry.weights) == set(MEMBERS)

    def test_invalid_weight_total_raises(self):
        with pytest.raises(RuntimeRegistryError, match="1.0"):
            RuntimeRegistry(weights={"ABACUS": 0.4, "ARTSTYLE": 0.2, "QPLANT": 0.2, "CODEX": 0.1})

    def test_missing_required_field_raises(self):
        registry = RuntimeRegistry()
        broken = dict(_runtime_records()["ABACUS"])
        broken.pop("truth_score")
        with pytest.raises(RuntimeRegistryError, match="truth_score"):
            registry.validate_record(broken)


class TestRuntimeRegistryBuild:
    def test_truth_matrix_contains_all_members(self):
        registry = RuntimeRegistry()
        truth_matrix = registry.build_truth_matrix(_runtime_records())
        assert [entry["member"] for entry in truth_matrix] == list(MEMBERS)

    def test_executed_is_derived_from_last_execution(self):
        registry = RuntimeRegistry()
        records = _runtime_records()
        records["ARTSTYLE"]["last_execution"] = None
        truth_matrix = registry.build_truth_matrix(records)
        artstyle = next(entry for entry in truth_matrix if entry["member"] == "ARTSTYLE")
        assert artstyle["executed"] is False

    def test_build_registry_record_contains_integrations(self):
        registry = RuntimeRegistry()
        rollup = FederationRollup().build_rollup_record(_repo_metrics(), runtime_records=_runtime_records())
        scree = FederationScree().build_scree_record(_repo_metrics(), runtime_records=_runtime_records())
        record = registry.build_registry_record(_runtime_records(), rollup=rollup, scree=scree)
        assert record["integrations"]["federation_rollup"]["geti"] == pytest.approx(0.7915)
        assert record["integrations"]["federation_scree"]["pc1"] == pytest.approx(0.413)

    def test_weighted_truth_score_uses_federation_weights(self):
        registry = RuntimeRegistry()
        record = registry.build_registry_record(_runtime_records())
        assert record["summary"]["weighted_truth_score"] == pytest.approx(0.766667, abs=1e-6)

    def test_build_report_lists_missing_validation_and_deployment(self):
        registry = RuntimeRegistry()
        report = registry.build_report(registry.build_registry_record(_runtime_records()))
        assert report["repos_missing_validation"] == ["ARTSTYLE"]
        assert report["repos_missing_deployment"] == ["ARTSTYLE", "QPLANT"]


class TestRuntimeRegistryWrite:
    def test_write_registry_writes_json(self, tmp_path: Path):
        registry = RuntimeRegistry()
        output = tmp_path / "runtime_registry.json"
        record = registry.write_registry(_runtime_records(), output)
        assert json.loads(output.read_text(encoding="utf-8")) == record

    def test_write_report_writes_json(self, tmp_path: Path):
        registry = RuntimeRegistry()
        record = registry.build_registry_record(_runtime_records())
        output = tmp_path / "runtime_registry_report.json"
        report = registry.write_report(record, output)
        assert json.loads(output.read_text(encoding="utf-8")) == report

    def test_generate_writes_both_outputs(self, tmp_path: Path):
        registry = RuntimeRegistry()
        runtime_dir = tmp_path / "runtime_registry"
        runtime_dir.mkdir()
        for member, record in _runtime_records().items():
            filename = f"{member.lower()}_runtime.json"
            (runtime_dir / filename).write_text(json.dumps(record, indent=2), encoding="utf-8")
        rollup_path = tmp_path / "federation_rollup.json"
        scree_path = tmp_path / "federation_scree.json"
        rollup_path.write_text(json.dumps(FederationRollup().build_rollup_record(_repo_metrics()), indent=2), encoding="utf-8")
        scree_path.write_text(json.dumps(FederationScree().build_scree_record(_repo_metrics()), indent=2), encoding="utf-8")
        registry_output = tmp_path / "runtime_registry.json"
        report_output = tmp_path / "runtime_registry_report.json"
        registry_record, report = registry.generate(
            runtime_dir=runtime_dir,
            registry_output_path=registry_output,
            report_output_path=report_output,
            rollup_path=rollup_path,
            scree_path=scree_path,
        )
        assert registry_record["summary"]["runtime_exists_count"] == 4
        assert report["repo_count"] == 4
        assert registry_output.exists()
        assert report_output.exists()


class TestFederationIntegration:
    def test_rollup_includes_runtime_status(self):
        record = FederationRollup().build_rollup_record(_repo_metrics(), runtime_records=_runtime_records())
        assert record["runtime_status"]["runtime_validated_count"] == 3
        assert record["runtime_status"]["truth_matrix"][0]["member"] == "ABACUS"

    def test_scree_includes_truth_matrix(self):
        record = FederationScree().build_scree_record(_repo_metrics(), runtime_records=_runtime_records())
        assert len(record["truth_matrix"]) == 4
        assert record["truth_matrix"][1]["member"] == "ARTSTYLE"


class TestRuntimeRegistryArtifacts:
    def test_runtime_source_files_exist(self):
        for member in MEMBERS:
            path = ROOT / DEFAULT_RUNTIME_DIR / f"{member.lower()}_runtime.json"
            assert path.exists(), f"Missing runtime source: {path}"

    def test_runtime_source_files_have_required_fields(self):
        for member in MEMBERS:
            path = ROOT / DEFAULT_RUNTIME_DIR / f"{member.lower()}_runtime.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            for field in REQUIRED_FIELDS:
                assert field in data, f"Missing {field} in {path.name}"

    def test_generated_runtime_registry_json_exists(self):
        path = ROOT / DEFAULT_REGISTRY_OUTPUT
        assert path.exists()
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["summary"]["runtime_exists_count"] == 4
        assert data["integrations"]["federation_rollup"]["geti"] == pytest.approx(0.7915)

    def test_generated_runtime_registry_report_json_exists(self):
        path = ROOT / DEFAULT_REPORT_OUTPUT
        assert path.exists()
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["runtime_validated_count"] == 3
        assert data["repos_missing_validation"] == ["ARTSTYLE"]

    def test_generated_rollup_and_scree_include_runtime_evidence(self):
        rollup_path = ROOT / "metrics" / "federation" / "federation_rollup.json"
        scree_path = ROOT / "metrics" / "federation" / "federation_scree.json"
        rollup = json.loads(rollup_path.read_text(encoding="utf-8"))
        scree = json.loads(scree_path.read_text(encoding="utf-8"))
        assert rollup["runtime_status"]["execution_count"] == 4
        assert len(scree["truth_matrix"]) == 4
