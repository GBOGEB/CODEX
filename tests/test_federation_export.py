"""Tests for src/qplant_presentation_engine/federation_export.py."""
from __future__ import annotations

import json
from pathlib import Path

from src.qplant_presentation_engine.federation_export import (
    FederationArtifactExporter,
    generate_federation_artifacts,
)


def _root() -> Path:
    return Path(__file__).resolve().parents[1]


def _metrics_dir() -> Path:
    return _root() / "metrics" / "repo"


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
