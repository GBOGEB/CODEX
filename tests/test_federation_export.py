"""Tests for src/qplant_presentation_engine/federation_export.py."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.qplant_presentation_engine.federation_export import (
    FederationArtifactExporter,
    FederationExportError,
    generate_federation_artifacts,
)


def _root() -> Path:
    return Path(__file__).resolve().parents[1]


def _metrics_dir() -> Path:
    return _root() / "metrics" / "repo"


def _copy_metrics_inputs(destination: Path) -> Path:
    source = _metrics_dir()
    destination.mkdir(parents=True, exist_ok=True)
    for name in ("abacus_metrics.json", "artstyle_metrics.json", "qplant_metrics.json", "codex_metrics.json"):
        (destination / name).write_text((source / name).read_text(encoding="utf-8"), encoding="utf-8")
    return destination


class TestFederationArtifactExport:
    def test_write_outputs_generates_all_required_files(self, tmp_path: Path):
        federation_dir = tmp_path / "metrics" / "federation"
        bottleneck_output = tmp_path / "bottleneck_report.json"

        rollup, scree, bottleneck = FederationArtifactExporter().write_outputs(
            metrics_dir=_metrics_dir(),
            federation_dir=federation_dir,
            bottleneck_output=bottleneck_output,
        )

        rollup_path = federation_dir / "federation_rollup.json"
        scree_path = federation_dir / "federation_scree.json"

        assert rollup_path.exists()
        assert scree_path.exists()
        assert bottleneck_output.exists()

        assert json.loads(rollup_path.read_text(encoding="utf-8")) == rollup
        assert json.loads(scree_path.read_text(encoding="utf-8")) == scree
        assert json.loads(bottleneck_output.read_text(encoding="utf-8")) == bottleneck

    def test_rollup_has_required_canonical_fields(self):
        repo_metrics = FederationArtifactExporter()._load_repo_metrics(_metrics_dir())
        rollup = FederationArtifactExporter().build_federation_rollup_export(repo_metrics)

        for key in (
            "forward_pca",
            "backward_pca",
            "geti",
            "pci",
            "expansion_factor",
            "repo_summaries",
        ):
            assert key in rollup
        assert len(rollup["repo_summaries"]) == 4

    def test_scree_has_pc1_to_pc5_with_variance_rank_and_cumulative(self):
        repo_metrics = FederationArtifactExporter()._load_repo_metrics(_metrics_dir())
        scree = FederationArtifactExporter().build_federation_scree_export(repo_metrics)

        for component in ("PC1", "PC2", "PC3", "PC4", "PC5"):
            assert component in scree
            assert "variance" in scree[component]
            assert "rank" in scree[component]
            assert "cumulative_variance" in scree[component]

    def test_bottleneck_report_has_required_fields(self):
        repo_metrics = FederationArtifactExporter()._load_repo_metrics(_metrics_dir())
        report = FederationArtifactExporter().build_bottleneck_report(repo_metrics)

        for key in (
            "dominant_repo",
            "dominant_wave",
            "dominant_bottleneck",
            "recommended_next_action",
            "timestamp",
        ):
            assert key in report

    def test_generate_federation_artifacts_uses_provided_paths(self, tmp_path: Path):
        federation_dir = tmp_path / "metrics" / "federation"
        bottleneck_output = tmp_path / "bottleneck_report.json"

        generate_federation_artifacts(
            metrics_dir=_metrics_dir(),
            federation_dir=federation_dir,
            bottleneck_output=bottleneck_output,
        )

        assert (federation_dir / "federation_rollup.json").exists()
        assert (federation_dir / "federation_scree.json").exists()
        assert bottleneck_output.exists()

    def test_rejects_duplicate_members(self, tmp_path: Path):
        federation_dir = tmp_path / "metrics" / "federation"
        bottleneck_output = tmp_path / "bottleneck_report.json"

        with pytest.raises(FederationExportError, match="canonical federation members"):
            FederationArtifactExporter(members=("ABACUS", "ABACUS", "ARTSTYLE", "QPLANT")).write_outputs(
                metrics_dir=_metrics_dir(),
                federation_dir=federation_dir,
                bottleneck_output=bottleneck_output,
            )

    def test_write_outputs_normalizes_member_order(self, tmp_path: Path):
        federation_dir = tmp_path / "metrics" / "federation"
        bottleneck_output = tmp_path / "bottleneck_report.json"

        rollup, scree, _ = FederationArtifactExporter(
            members=("CODEX", "QPLANT", "ABACUS", "ARTSTYLE")
        ).write_outputs(
            metrics_dir=_metrics_dir(),
            federation_dir=federation_dir,
            bottleneck_output=bottleneck_output,
        )

        assert rollup["members"] == ["ABACUS", "ARTSTYLE", "QPLANT", "CODEX"]
        assert [entry["member"] for entry in rollup["repo_summaries"]] == ["ABACUS", "ARTSTYLE", "QPLANT", "CODEX"]
        assert scree["members"] == ["ABACUS", "ARTSTYLE", "QPLANT", "CODEX"]

    def test_rejects_bool_in_federation_metrics(self, tmp_path: Path):
        corrupted_metrics_dir = _copy_metrics_inputs(tmp_path / "metrics")
        abacus_path = corrupted_metrics_dir / "abacus_metrics.json"
        data = json.loads(abacus_path.read_text(encoding="utf-8"))
        data["metrics"]["geti"] = True
        abacus_path.write_text(json.dumps(data), encoding="utf-8")

        exporter = FederationArtifactExporter()
        repo_metrics = exporter._load_repo_metrics(corrupted_metrics_dir)

        with pytest.raises(FederationExportError, match="Invalid geti for ABACUS"):
            exporter.build_federation_rollup_export(repo_metrics)

    def test_load_repo_metrics_rejects_malformed_json(self, tmp_path: Path):
        corrupted_metrics_dir = _copy_metrics_inputs(tmp_path / "metrics")
        (corrupted_metrics_dir / "abacus_metrics.json").write_text("{", encoding="utf-8")

        with pytest.raises(FederationExportError, match="Invalid repository metrics JSON for ABACUS"):
            FederationArtifactExporter()._load_repo_metrics(corrupted_metrics_dir)

    def test_load_repo_metrics_rejects_non_object_payload(self, tmp_path: Path):
        corrupted_metrics_dir = _copy_metrics_inputs(tmp_path / "metrics")
        (corrupted_metrics_dir / "abacus_metrics.json").write_text("[]", encoding="utf-8")

        with pytest.raises(FederationExportError, match="expected JSON object"):
            FederationArtifactExporter()._load_repo_metrics(corrupted_metrics_dir)

    def test_rollup_rejects_bool_in_pca_variance_explained(self, tmp_path: Path):
        corrupted_metrics_dir = _copy_metrics_inputs(tmp_path / "metrics")
        abacus_path = corrupted_metrics_dir / "abacus_metrics.json"
        data = json.loads(abacus_path.read_text(encoding="utf-8"))
        data["metrics"]["forward_pca"]["variance_explained"][0] = True
        abacus_path.write_text(json.dumps(data), encoding="utf-8")

        repo_metrics = FederationArtifactExporter()._load_repo_metrics(corrupted_metrics_dir)

        with pytest.raises(FederationExportError, match="forward_pca.variance_explained"):
            FederationArtifactExporter().build_federation_rollup_export(repo_metrics)

    def test_scree_rejects_bool_component_values(self, tmp_path: Path):
        corrupted_metrics_dir = _copy_metrics_inputs(tmp_path / "metrics")
        abacus_path = corrupted_metrics_dir / "abacus_metrics.json"
        data = json.loads(abacus_path.read_text(encoding="utf-8"))
        data["metrics"]["scree"]["pc1"] = False
        abacus_path.write_text(json.dumps(data), encoding="utf-8")

        repo_metrics = FederationArtifactExporter()._load_repo_metrics(corrupted_metrics_dir)

        with pytest.raises(FederationExportError, match="Invalid scree.pc1 for ABACUS"):
            FederationArtifactExporter().build_federation_scree_export(repo_metrics)

    def test_bottleneck_wraps_aggregation_errors(self, tmp_path: Path):
        corrupted_metrics_dir = _copy_metrics_inputs(tmp_path / "metrics")
        abacus_path = corrupted_metrics_dir / "abacus_metrics.json"
        data = json.loads(abacus_path.read_text(encoding="utf-8"))
        del data["metrics"]["geti"]
        abacus_path.write_text(json.dumps(data), encoding="utf-8")

        repo_metrics = FederationArtifactExporter()._load_repo_metrics(corrupted_metrics_dir)

        with pytest.raises(FederationExportError, match="Failed to build bottleneck report"):
            FederationArtifactExporter().build_bottleneck_report(repo_metrics)

    def test_bottleneck_injectable_timestamp(self):
        repo_metrics = FederationArtifactExporter()._load_repo_metrics(_metrics_dir())
        fixed_ts = "2026-01-01T00:00:00Z"
        report = FederationArtifactExporter().build_bottleneck_report(
            repo_metrics, generated_at=fixed_ts
        )
        assert report["timestamp"] == fixed_ts

    def test_write_outputs_json_sorted_keys(self, tmp_path: Path):
        federation_dir = tmp_path / "metrics" / "federation"
        bottleneck_output = tmp_path / "bottleneck_report.json"

        FederationArtifactExporter().write_outputs(
            metrics_dir=_metrics_dir(),
            federation_dir=federation_dir,
            bottleneck_output=bottleneck_output,
        )

        for path in [
            federation_dir / "federation_rollup.json",
            federation_dir / "federation_scree.json",
            bottleneck_output,
        ]:
            raw = path.read_text(encoding="utf-8")
            parsed = json.loads(raw)
            assert raw == json.dumps(parsed, indent=2, sort_keys=True) + "\n" or raw == json.dumps(parsed, indent=2, sort_keys=True)
