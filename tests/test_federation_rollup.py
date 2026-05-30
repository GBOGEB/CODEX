"""Tests for src/qplant_presentation_engine/federation_rollup.py."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.qplant_presentation_engine.federation_rollup import (
    DEFAULT_WEIGHTS,
    MEMBERS,
    SCALAR_METRICS,
    FederationRollup,
    FederationRollupError,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _repo_metrics() -> dict:
    """Minimal repo metrics matching the metrics/repo/*.json structure."""
    return {
        "ABACUS": {
            "metrics": {
                "forward_pca": {
                    "variance_explained": [0.42, 0.26, 0.17, 0.10, 0.05],
                    "convergence_score": 0.84,
                },
                "backward_pca": {
                    "variance_explained": [0.40, 0.27, 0.18, 0.10, 0.05],
                    "regression_score": 0.81,
                },
                "geti": 0.82,
                "pci": 0.79,
                "expansion_factor": 1.18,
                "scree": {"pc1": 0.42, "pc2": 0.26, "pc3": 0.17, "pc4": 0.10, "pc5": 0.05},
            }
        },
        "ARTSTYLE": {
            "metrics": {
                "forward_pca": {
                    "variance_explained": [0.38, 0.28, 0.19, 0.10, 0.05],
                    "convergence_score": 0.73,
                },
                "backward_pca": {
                    "variance_explained": [0.36, 0.29, 0.20, 0.10, 0.05],
                    "regression_score": 0.70,
                },
                "geti": 0.71,
                "pci": 0.68,
                "expansion_factor": 1.22,
                "scree": {"pc1": 0.38, "pc2": 0.28, "pc3": 0.19, "pc4": 0.10, "pc5": 0.05},
            }
        },
        "QPLANT": {
            "metrics": {
                "forward_pca": {
                    "variance_explained": [0.44, 0.24, 0.18, 0.09, 0.05],
                    "convergence_score": 0.79,
                },
                "backward_pca": {
                    "variance_explained": [0.41, 0.25, 0.20, 0.09, 0.05],
                    "regression_score": 0.75,
                },
                "geti": 0.77,
                "pci": 0.74,
                "expansion_factor": 1.15,
                "scree": {"pc1": 0.44, "pc2": 0.24, "pc3": 0.18, "pc4": 0.09, "pc5": 0.05},
            }
        },
        "CODEX": {
            "metrics": {
                "forward_pca": {
                    "variance_explained": [0.40, 0.27, 0.18, 0.10, 0.05],
                    "convergence_score": 0.87,
                },
                "backward_pca": {
                    "variance_explained": [0.38, 0.28, 0.19, 0.10, 0.05],
                    "regression_score": 0.84,
                },
                "geti": 0.85,
                "pci": 0.83,
                "expansion_factor": 1.12,
                "scree": {"pc1": 0.40, "pc2": 0.27, "pc3": 0.18, "pc4": 0.10, "pc5": 0.05},
            }
        },
    }


def _write_runtime_registry(tmp_path: Path) -> Path:
    """Write a temporary runtime registry directory."""
    registry_dir = tmp_path / "runtime_registry"
    registry_dir.mkdir(parents=True, exist_ok=True)
    records = {
        "abacus_runtime.json": "ABACUS",
        "artstyle_runtime.json": "ARTSTYLE",
        "qplant_runtime.json": "QPLANT",
        "codex_runtime.json": "CODEX",
    }
    for filename, repo in records.items():
        (registry_dir / filename).write_text(
            json.dumps(
                {
                    "repo": repo,
                    "runtime_exists": True,
                    "runtime_validated": True,
                    "deployment_exists": True,
                    "last_execution": "2026-05-30T18:07:45Z",
                    "last_validation": "2026-05-30T18:07:45Z",
                    "last_deployment": "2026-05-30T18:07:45Z",
                    "truth_score": 0.99,
                }
            ),
            encoding="utf-8",
        )
    return registry_dir


# ---------------------------------------------------------------------------
# Weight validation
# ---------------------------------------------------------------------------

class TestWeightValidation:
    def test_default_weights_accepted(self):
        rollup = FederationRollup()
        assert set(rollup.weights.keys()) == set(MEMBERS)

    def test_custom_weights_accepted(self):
        weights = {"ABACUS": 0.25, "ARTSTYLE": 0.25, "QPLANT": 0.25, "CODEX": 0.25}
        rollup = FederationRollup(weights=weights)
        assert rollup.weights == weights

    def test_weights_not_summing_to_one_raises(self):
        bad = {"ABACUS": 0.30, "ARTSTYLE": 0.20, "QPLANT": 0.25, "CODEX": 0.20}
        with pytest.raises(FederationRollupError, match="1.0"):
            FederationRollup(weights=bad)

    def test_missing_member_weight_raises(self):
        bad = {"ABACUS": 0.40, "ARTSTYLE": 0.30, "QPLANT": 0.30}
        with pytest.raises(FederationRollupError, match="CODEX"):
            FederationRollup(weights=bad)


# ---------------------------------------------------------------------------
# aggregate()
# ---------------------------------------------------------------------------

class TestAggregate:
    def test_returns_all_scalar_metrics(self):
        rollup = FederationRollup()
        result = rollup.aggregate(_repo_metrics())
        for key in SCALAR_METRICS:
            assert key in result

    def test_returns_forward_and_backward_pca(self):
        rollup = FederationRollup()
        result = rollup.aggregate(_repo_metrics())
        assert "forward_pca" in result
        assert "backward_pca" in result

    def test_geti_weighted_average(self):
        rollup = FederationRollup()
        result = rollup.aggregate(_repo_metrics())
        expected = (0.35 * 0.82 + 0.20 * 0.71 + 0.25 * 0.77 + 0.20 * 0.85)
        assert abs(result["geti"] - expected) < 1e-5

    def test_pci_weighted_average(self):
        rollup = FederationRollup()
        result = rollup.aggregate(_repo_metrics())
        expected = (0.35 * 0.79 + 0.20 * 0.68 + 0.25 * 0.74 + 0.20 * 0.83)
        assert abs(result["pci"] - expected) < 1e-5

    def test_expansion_factor_weighted_average(self):
        rollup = FederationRollup()
        result = rollup.aggregate(_repo_metrics())
        expected = (0.35 * 1.18 + 0.20 * 1.22 + 0.25 * 1.15 + 0.20 * 1.12)
        assert abs(result["expansion_factor"] - expected) < 1e-5

    def test_forward_pca_convergence_score_weighted(self):
        rollup = FederationRollup()
        result = rollup.aggregate(_repo_metrics())
        expected = (0.35 * 0.84 + 0.20 * 0.73 + 0.25 * 0.79 + 0.20 * 0.87)
        assert abs(result["forward_pca"]["convergence_score"] - expected) < 1e-5

    def test_backward_pca_regression_score_weighted(self):
        rollup = FederationRollup()
        result = rollup.aggregate(_repo_metrics())
        expected = (0.35 * 0.81 + 0.20 * 0.70 + 0.25 * 0.75 + 0.20 * 0.84)
        assert abs(result["backward_pca"]["regression_score"] - expected) < 1e-5

    def test_forward_pca_variance_has_five_components(self):
        rollup = FederationRollup()
        result = rollup.aggregate(_repo_metrics())
        assert len(result["forward_pca"]["variance_explained"]) == 5

    def test_backward_pca_variance_has_five_components(self):
        rollup = FederationRollup()
        result = rollup.aggregate(_repo_metrics())
        assert len(result["backward_pca"]["variance_explained"]) == 5

    def test_missing_member_raises(self):
        metrics = _repo_metrics()
        del metrics["QPLANT"]
        rollup = FederationRollup()
        with pytest.raises(FederationRollupError, match="QPLANT"):
            rollup.aggregate(metrics)

    def test_equal_weights_produce_simple_average(self):
        weights = {"ABACUS": 0.25, "ARTSTYLE": 0.25, "QPLANT": 0.25, "CODEX": 0.25}
        rollup = FederationRollup(weights=weights)
        result = rollup.aggregate(_repo_metrics())
        expected_geti = (0.82 + 0.71 + 0.77 + 0.85) / 4
        assert abs(result["geti"] - expected_geti) < 1e-5


# ---------------------------------------------------------------------------
# compute_bottleneck()
# ---------------------------------------------------------------------------

class TestComputeBottleneck:
    def test_returns_required_keys(self):
        rollup = FederationRollup()
        metrics = _repo_metrics()
        aggregate = rollup.aggregate(metrics)
        report = rollup.compute_bottleneck(metrics, aggregate)
        for key in ("wave", "subwave", "threshold_factor", "bottleneck_count", "bottlenecks"):
            assert key in report

    def test_artstyle_flagged_on_geti_and_pci(self):
        rollup = FederationRollup()
        metrics = _repo_metrics()
        aggregate = rollup.aggregate(metrics)
        report = rollup.compute_bottleneck(metrics, aggregate)
        members_flagged = {entry["member"] for entry in report["bottlenecks"]}
        assert "ARTSTYLE" in members_flagged

    def test_bottleneck_count_matches_list_length(self):
        rollup = FederationRollup()
        metrics = _repo_metrics()
        aggregate = rollup.aggregate(metrics)
        report = rollup.compute_bottleneck(metrics, aggregate)
        assert report["bottleneck_count"] == len(report["bottlenecks"])

    def test_no_bottleneck_with_zero_threshold(self):
        rollup = FederationRollup()
        metrics = _repo_metrics()
        aggregate = rollup.aggregate(metrics)
        report = rollup.compute_bottleneck(metrics, aggregate, threshold_factor=0.0)
        assert report["bottleneck_count"] == 0

    def test_all_bottleneck_with_threshold_above_max(self):
        rollup = FederationRollup()
        metrics = _repo_metrics()
        aggregate = rollup.aggregate(metrics)
        report = rollup.compute_bottleneck(metrics, aggregate, threshold_factor=2.0)
        assert report["bottleneck_count"] == len(MEMBERS)

    def test_bottleneck_entry_contains_member_flags_weight(self):
        rollup = FederationRollup()
        metrics = _repo_metrics()
        aggregate = rollup.aggregate(metrics)
        report = rollup.compute_bottleneck(metrics, aggregate)
        for entry in report["bottlenecks"]:
            assert "member" in entry
            assert "flags" in entry
            assert "weight" in entry


# ---------------------------------------------------------------------------
# build_rollup_record()
# ---------------------------------------------------------------------------

class TestBuildRollupRecord:
    def test_contains_required_top_level_keys(self):
        rollup = FederationRollup()
        record = rollup.build_rollup_record(_repo_metrics())
        for key in ("wave", "subwave", "members", "weights", "aggregated"):
            assert key in record

    def test_members_list_matches_constants(self):
        rollup = FederationRollup()
        record = rollup.build_rollup_record(_repo_metrics())
        assert record["members"] == list(MEMBERS)

    def test_wave_defaults(self):
        rollup = FederationRollup()
        record = rollup.build_rollup_record(_repo_metrics())
        assert record["wave"] == "W007"
        assert record["subwave"] == "W007.1"

    def test_custom_wave_overrides(self):
        rollup = FederationRollup()
        record = rollup.build_rollup_record(_repo_metrics(), wave="W008", subwave="W008.2")
        assert record["wave"] == "W008"
        assert record["subwave"] == "W008.2"

    def test_includes_runtime_registry_when_directory_provided(self, tmp_path: Path):
        rollup = FederationRollup()
        registry_dir = _write_runtime_registry(tmp_path)
        record = rollup.build_rollup_record(_repo_metrics(), runtime_registry_dir=registry_dir)
        assert set(record["runtime_registry"].keys()) == set(MEMBERS)
        assert record["runtime_status"]["runtime_exists"] is True
        assert record["runtime_status"]["runtime_validated"] is True
        assert record["runtime_status"]["deployment_exists"] is True


# ---------------------------------------------------------------------------
# write_rollup()
# ---------------------------------------------------------------------------

class TestWriteRollup:
    def test_writes_valid_json(self, tmp_path: Path):
        rollup = FederationRollup()
        output = tmp_path / "federation_rollup.json"
        record = rollup.write_rollup(_repo_metrics(), output)
        parsed = json.loads(output.read_text(encoding="utf-8"))
        assert parsed == record

    def test_creates_parent_directories(self, tmp_path: Path):
        rollup = FederationRollup()
        output = tmp_path / "deep" / "nested" / "rollup.json"
        rollup.write_rollup(_repo_metrics(), output)
        assert output.exists()

    def test_returned_record_matches_written_file(self, tmp_path: Path):
        rollup = FederationRollup()
        output = tmp_path / "rollup.json"
        returned = rollup.write_rollup(_repo_metrics(), output)
        written = json.loads(output.read_text(encoding="utf-8"))
        assert returned == written


# ---------------------------------------------------------------------------
# write_bottleneck_report()
# ---------------------------------------------------------------------------

class TestWriteBottleneckReport:
    def test_writes_valid_json(self, tmp_path: Path):
        rollup = FederationRollup()
        output = tmp_path / "bottleneck_report.json"
        report = rollup.write_bottleneck_report(_repo_metrics(), output)
        parsed = json.loads(output.read_text(encoding="utf-8"))
        assert parsed == report

    def test_creates_parent_directories(self, tmp_path: Path):
        rollup = FederationRollup()
        output = tmp_path / "reports" / "bottleneck_report.json"
        rollup.write_bottleneck_report(_repo_metrics(), output)
        assert output.exists()

    def test_written_file_contains_bottleneck_count(self, tmp_path: Path):
        rollup = FederationRollup()
        output = tmp_path / "bottleneck_report.json"
        rollup.write_bottleneck_report(_repo_metrics(), output)
        data = json.loads(output.read_text(encoding="utf-8"))
        assert "bottleneck_count" in data


# ---------------------------------------------------------------------------
# Integration: metrics JSON files are readable and produce valid rollup
# ---------------------------------------------------------------------------

class TestMetricsJsonFiles:
    def test_repo_metrics_files_exist(self):
        root = Path(__file__).resolve().parents[1]
        for name in ("abacus_metrics", "artstyle_metrics", "qplant_metrics", "codex_metrics"):
            path = root / "metrics" / "repo" / f"{name}.json"
            assert path.exists(), f"Missing: {path}"

    def test_repo_metrics_files_parse_correctly(self):
        root = Path(__file__).resolve().parents[1]
        name_to_member = {
            "abacus_metrics": "ABACUS",
            "artstyle_metrics": "ARTSTYLE",
            "qplant_metrics": "QPLANT",
            "codex_metrics": "CODEX",
        }
        loaded: dict = {}
        for filename, member in name_to_member.items():
            path = root / "metrics" / "repo" / f"{filename}.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            loaded[member] = data

        rollup = FederationRollup()
        record = rollup.build_rollup_record(loaded)
        assert record["wave"] == "W007"
        assert set(record["members"]) == set(MEMBERS)
        assert 0 < record["aggregated"]["geti"] < 1
        assert 0 < record["aggregated"]["pci"] < 1

    def test_federation_rollup_json_parseable(self):
        root = Path(__file__).resolve().parents[1]
        path = root / "metrics" / "federation" / "federation_rollup.json"
        assert path.exists()
        data = json.loads(path.read_text(encoding="utf-8"))
        assert "aggregated" in data
        assert "geti" in data["aggregated"]
