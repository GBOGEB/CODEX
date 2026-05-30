"""Tests for src/qplant_presentation_engine/federation_scree.py."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.qplant_presentation_engine.federation_scree import (
    COMPONENTS,
    DEFAULT_WEIGHTS,
    MEMBERS,
    FederationScree,
    FederationScreeError,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _repo_metrics() -> dict:
    """Minimal repo metrics matching the metrics/repo/*.json structure."""
    return {
        "ABACUS": {
            "metrics": {
                "scree": {"pc1": 0.42, "pc2": 0.26, "pc3": 0.17, "pc4": 0.10, "pc5": 0.05},
            }
        },
        "ARTSTYLE": {
            "metrics": {
                "scree": {"pc1": 0.38, "pc2": 0.28, "pc3": 0.19, "pc4": 0.10, "pc5": 0.05},
            }
        },
        "QPLANT": {
            "metrics": {
                "scree": {"pc1": 0.44, "pc2": 0.24, "pc3": 0.18, "pc4": 0.09, "pc5": 0.05},
            }
        },
        "CODEX": {
            "metrics": {
                "scree": {"pc1": 0.40, "pc2": 0.27, "pc3": 0.18, "pc4": 0.10, "pc5": 0.05},
            }
        },
    }


# ---------------------------------------------------------------------------
# aggregate_scree()
# ---------------------------------------------------------------------------

class TestAggregateScree:
    def test_returns_all_components(self):
        scree = FederationScree()
        result = scree.aggregate_scree(_repo_metrics())
        for c in COMPONENTS:
            assert c in result

    def test_pc1_weighted_average(self):
        scree = FederationScree()
        result = scree.aggregate_scree(_repo_metrics())
        expected = 0.35 * 0.42 + 0.20 * 0.38 + 0.25 * 0.44 + 0.20 * 0.40
        assert abs(result["pc1"] - expected) < 1e-5

    def test_pc2_weighted_average(self):
        scree = FederationScree()
        result = scree.aggregate_scree(_repo_metrics())
        expected = 0.35 * 0.26 + 0.20 * 0.28 + 0.25 * 0.24 + 0.20 * 0.27
        assert abs(result["pc2"] - expected) < 1e-5

    def test_pc5_all_equal_to_0_05(self):
        scree = FederationScree()
        result = scree.aggregate_scree(_repo_metrics())
        assert abs(result["pc5"] - 0.05) < 1e-5

    def test_missing_member_raises(self):
        metrics = _repo_metrics()
        del metrics["CODEX"]
        scree = FederationScree()
        with pytest.raises(FederationScreeError, match="CODEX"):
            scree.aggregate_scree(metrics)

    def test_missing_scree_key_raises(self):
        metrics = _repo_metrics()
        metrics["ABACUS"] = {"metrics": {"geti": 0.8}}
        scree = FederationScree()
        with pytest.raises(FederationScreeError, match="scree"):
            scree.aggregate_scree(metrics)

    def test_equal_weights_produce_simple_average(self):
        weights = {"ABACUS": 0.25, "ARTSTYLE": 0.25, "QPLANT": 0.25, "CODEX": 0.25}
        scree = FederationScree(weights=weights)
        result = scree.aggregate_scree(_repo_metrics())
        expected_pc1 = (0.42 + 0.38 + 0.44 + 0.40) / 4
        assert abs(result["pc1"] - expected_pc1) < 1e-5

    def test_all_values_non_negative(self):
        scree = FederationScree()
        result = scree.aggregate_scree(_repo_metrics())
        for c in COMPONENTS:
            assert result[c] >= 0.0


# ---------------------------------------------------------------------------
# rank_components()
# ---------------------------------------------------------------------------

class TestRankComponents:
    def test_returns_list_of_tuples(self):
        scree = FederationScree()
        aggregated = scree.aggregate_scree(_repo_metrics())
        ranked = scree.rank_components(aggregated)
        assert isinstance(ranked, list)
        assert all(isinstance(item, tuple) and len(item) == 2 for item in ranked)

    def test_sorted_descending(self):
        scree = FederationScree()
        aggregated = scree.aggregate_scree(_repo_metrics())
        ranked = scree.rank_components(aggregated)
        values = [v for _, v in ranked]
        assert values == sorted(values, reverse=True)

    def test_pc1_is_first(self):
        scree = FederationScree()
        aggregated = scree.aggregate_scree(_repo_metrics())
        ranked = scree.rank_components(aggregated)
        assert ranked[0][0] == "pc1"

    def test_pc5_is_last(self):
        scree = FederationScree()
        aggregated = scree.aggregate_scree(_repo_metrics())
        ranked = scree.rank_components(aggregated)
        assert ranked[-1][0] == "pc5"

    def test_all_components_present(self):
        scree = FederationScree()
        aggregated = scree.aggregate_scree(_repo_metrics())
        ranked = scree.rank_components(aggregated)
        assert {c for c, _ in ranked} == set(COMPONENTS)


# ---------------------------------------------------------------------------
# cumulative_variance()
# ---------------------------------------------------------------------------

class TestCumulativeVariance:
    def test_returns_dict_with_all_components(self):
        scree = FederationScree()
        aggregated = scree.aggregate_scree(_repo_metrics())
        cumulative = scree.cumulative_variance(aggregated)
        assert set(cumulative.keys()) == set(COMPONENTS)

    def test_last_value_is_total_sum(self):
        scree = FederationScree()
        aggregated = scree.aggregate_scree(_repo_metrics())
        total = sum(aggregated.values())
        cumulative = scree.cumulative_variance(aggregated)
        last_value = max(cumulative.values())
        assert abs(last_value - total) < 1e-5

    def test_values_are_monotonically_non_decreasing(self):
        scree = FederationScree()
        aggregated = scree.aggregate_scree(_repo_metrics())
        cumulative = scree.cumulative_variance(aggregated)
        ranked = scree.rank_components(aggregated)
        values = [cumulative[c] for c, _ in ranked]
        assert values == sorted(values)


# ---------------------------------------------------------------------------
# build_scree_record()
# ---------------------------------------------------------------------------

class TestBuildScreeRecord:
    def test_contains_required_top_level_keys(self):
        scree = FederationScree()
        record = scree.build_scree_record(_repo_metrics())
        for key in (
            "wave", "subwave", "members", "weights",
            "federation_scree", "ranked_components", "cumulative_variance",
            "per_member_scree",
        ):
            assert key in record

    def test_ranked_components_are_dicts_with_component_and_variance(self):
        scree = FederationScree()
        record = scree.build_scree_record(_repo_metrics())
        for entry in record["ranked_components"]:
            assert "component" in entry
            assert "variance_explained" in entry

    def test_per_member_scree_covers_all_members(self):
        scree = FederationScree()
        record = scree.build_scree_record(_repo_metrics())
        assert set(record["per_member_scree"].keys()) == set(MEMBERS)

    def test_wave_defaults(self):
        scree = FederationScree()
        record = scree.build_scree_record(_repo_metrics())
        assert record["wave"] == "W007"
        assert record["subwave"] == "W007.1"

    def test_custom_wave_overrides(self):
        scree = FederationScree()
        record = scree.build_scree_record(_repo_metrics(), wave="W008", subwave="W008.2")
        assert record["wave"] == "W008"
        assert record["subwave"] == "W008.2"

    def test_federation_scree_matches_aggregate(self):
        scree = FederationScree()
        metrics = _repo_metrics()
        record = scree.build_scree_record(metrics)
        aggregated = scree.aggregate_scree(metrics)
        assert record["federation_scree"] == aggregated


# ---------------------------------------------------------------------------
# write_scree()
# ---------------------------------------------------------------------------

class TestWriteScree:
    def test_writes_valid_json(self, tmp_path: Path):
        scree = FederationScree()
        output = tmp_path / "federation_scree.json"
        record = scree.write_scree(_repo_metrics(), output)
        parsed = json.loads(output.read_text(encoding="utf-8"))
        assert parsed == record

    def test_creates_parent_directories(self, tmp_path: Path):
        scree = FederationScree()
        output = tmp_path / "deep" / "nested" / "scree.json"
        scree.write_scree(_repo_metrics(), output)
        assert output.exists()

    def test_returned_record_matches_written_file(self, tmp_path: Path):
        scree = FederationScree()
        output = tmp_path / "scree.json"
        returned = scree.write_scree(_repo_metrics(), output)
        written = json.loads(output.read_text(encoding="utf-8"))
        assert returned == written


# ---------------------------------------------------------------------------
# Integration: metrics JSON files
# ---------------------------------------------------------------------------

class TestMetricsJsonFiles:
    def test_repo_metrics_files_have_scree_key(self):
        root = Path(__file__).resolve().parents[1]
        name_to_member = {
            "abacus_metrics": "ABACUS",
            "artstyle_metrics": "ARTSTYLE",
            "qplant_metrics": "QPLANT",
            "codex_metrics": "CODEX",
        }
        for filename in name_to_member:
            path = root / "metrics" / "repo" / f"{filename}.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            assert "scree" in data["metrics"], f"Missing scree in {filename}"

    def test_scree_analysis_from_repo_json_files(self):
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
            loaded[member] = json.loads(path.read_text(encoding="utf-8"))

        scree = FederationScree()
        record = scree.build_scree_record(loaded)
        assert record["wave"] == "W007"
        assert len(record["ranked_components"]) == 5
        assert record["ranked_components"][0]["component"] == "pc1"

    def test_federation_scree_json_parseable(self):
        root = Path(__file__).resolve().parents[1]
        path = root / "metrics" / "federation" / "federation_scree.json"
        assert path.exists()
        data = json.loads(path.read_text(encoding="utf-8"))
        assert "federation_scree" in data
        assert "pc1" in data["federation_scree"]


def _runtime_records() -> dict:
    return {
        member: {
            "repo": f"GBOGEB/{member}",
            "runtime_exists": True,
            "runtime_validated": True,
            "deployment_exists": True,
            "last_execution": "2026-05-30T09:00:00Z",
            "last_validation": "2026-05-30T10:00:00Z",
            "last_deployment": "2026-05-30T11:00:00Z",
            "truth_score": 0.9,
        }
        for member in MEMBERS
    }


class TestBuildTruthMatrix:
    def test_valid_records_return_matrix(self):
        matrix = FederationScree.build_truth_matrix(_runtime_records())
        assert len(matrix) == 4
        assert matrix[0]["member"] == "ABACUS"

    def test_none_truth_score_raises_federation_scree_error(self):
        records = _runtime_records()
        records["ABACUS"]["truth_score"] = None
        with pytest.raises(FederationScreeError, match="truth_score"):
            FederationScree.build_truth_matrix(records)

    def test_non_numeric_truth_score_raises_federation_scree_error(self):
        records = _runtime_records()
        records["CODEX"]["truth_score"] = "not-a-number"
        with pytest.raises(FederationScreeError, match="truth_score"):
            FederationScree.build_truth_matrix(records)

    def test_missing_member_raises_federation_scree_error(self):
        records = _runtime_records()
        del records["ARTSTYLE"]
        with pytest.raises(FederationScreeError, match="ARTSTYLE"):
            FederationScree.build_truth_matrix(records)
