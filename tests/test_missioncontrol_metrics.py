import json
from pathlib import Path

from scripts.build_missioncontrol_metrics import (
    STATUS_DERIVED,
    STATUS_WITHHELD,
    apply_source_status_overlay,
    bt_rank,
    build_snapshot,
    pressure_metric,
)

ROOT = Path(__file__).resolve().parents[1]


def test_pressure_renormalizes_only_measured_inputs() -> None:
    result = pressure_metric(
        {"urgency": 1.0, "downstream_blocks": 2, "proof_deficit": 1.0},
        {"urgency": 0.3, "criticality": 0.2, "downstream_blocks": 0.2, "unblock_value": 0.15, "proof_deficit": 0.1, "age": 0.05},
    )
    assert result["status"] == STATUS_DERIVED
    assert result["coverage"] == 0.5
    assert set(result["missing_inputs"]) == {"age", "criticality", "unblock_value"}


def test_bt_withholds_without_observed_outcomes() -> None:
    assert bt_rank([])["status"] == STATUS_WITHHELD


def test_snapshot_uses_same_graph_for_all_projections() -> None:
    graph = json.loads((ROOT / "mission_control/mycelium/interaction_graph.json").read_text())
    obs = json.loads((ROOT / "mission_control/mycelium/control_observations.json").read_text())
    snapshot = build_snapshot(graph, obs)
    assert snapshot["guards"]["same_graph_multiple_projections"] is True
    assert snapshot["graph"]["node_count"] == len(graph["nodes"])
    assert snapshot["projections"]["engineering"]["nodes"] > 0
    assert snapshot["projections"]["control"]["nodes"] > 0
    assert snapshot["projections"]["observability"]["nodes"] > 0


def test_latest_abacus_source_status_supersedes_stale_observation_metrics() -> None:
    snapshot = {
        "nodes": {
            "dab_mech": {
                "mechanical_progress": {
                    "status": "MEASURED",
                    "residual_w293": 3598,
                    "evidence_pr": "#1494",
                }
            },
            "dab_hard": {
                "family_progress": [
                    {"family": "E741", "baseline": 38, "measured_postmerge": 40},
                    {"family": "F811", "baseline": 15, "measured_postmerge": 16},
                    {"family": "E999", "baseline": 6, "measured_postmerge": 1},
                ]
            },
        }
    }
    source_status = {
        "sources": [
            {
                "id": "abacus",
                "repository": "GBOGEB/ABACUS",
                "head_sha": "current",
                "census_pr": 1501,
                "census_job": 109883686239,
                "census_total": 9764,
                "census_artifact_id": 11095916691,
                "census_artifact_sha256": "digest",
                "evidence_ref": "typed-return.json",
                "w293_postmerge_status": "MEASURED_BY_PR1501_CENSUS",
                "source_bound_hold": "qplant/source_bound.py",
                "family_slice_baselines": {"E741": 40},
                "E999": 1,
                "F821": 0,
                "F601": 0,
                "F811": 0,
                "F841": 77,
                "E722": 26,
                "E731": 0,
                "E741": 35,
                "W293": 1912,
            }
        ]
    }

    apply_source_status_overlay(snapshot, source_status)

    mech = snapshot["nodes"]["dab_mech"]["mechanical_progress"]
    assert mech["residual_w293"] == 1912
    assert mech["repository_total_flake8"] == 9764
    assert mech["evidence_pr"] == "#1501"

    hard = {
        row["family"]: row
        for row in snapshot["nodes"]["dab_hard"]["family_progress"]
    }
    assert hard["E741"]["baseline"] == 40
    assert hard["E741"]["measured_postmerge"] == 35
    assert hard["E741"]["delta_from_baseline"] == -5
    assert hard["F811"]["measured_postmerge"] == 0
    assert hard["F811"]["state"] == "CLOSED"
    assert hard["E999"]["state"] == "SOURCE_BOUND_HOLD"
    assert snapshot["latest_remote_return"]["source_sha"] == "current"
