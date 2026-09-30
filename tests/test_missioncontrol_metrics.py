import json
from pathlib import Path

from scripts.build_missioncontrol_metrics import (
    STATUS_DERIVED,
    STATUS_WITHHELD,
    bt_rank,
    build_snapshot,
    pressure_metric,
    source_identity_is_measured,
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


def test_source_identity_measurement_requires_exact_head() -> None:
    assert source_identity_is_measured(
        {"status": "FRESH", "identity_status": "MEASURED", "head_sha": "abc"}
    )
    assert source_identity_is_measured(
        {"status": "MEASURED_CHAT_CONNECTOR", "head_sha": "abc"}
    )
    assert not source_identity_is_measured(
        {"status": "FRESH", "identity_status": "WITHHELD_HEAD_PROBE_ERROR"}
    )
    assert not source_identity_is_measured(
        {"status": "FRESH", "identity_status": "MEASURED"}
    )
