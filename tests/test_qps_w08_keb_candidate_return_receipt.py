from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "feedback" / "qps_w08_keb_candidate_return_receipt.yaml"
REQUEST = ROOT / "feedback" / "qps_w08_lifecycle_coverage_semantic_request.yaml"


def load(path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_receipt_is_candidate_only_and_child_owned_for_disposition():
    data = load(RECEIPT)
    assert data["candidate_state"] == "CANDIDATE_ONLY"
    assert data["child_disposition"] == "UNSET"
    controls = data["control_boundary"]
    assert controls["parent_credit_promotion_allowed"] is False
    assert controls["child_acceptance_required"] is True
    assert controls["missing_hash_inference_allowed"] is False
    assert controls["formal_completion_delta"] == 0
    assert controls["bidder_compliance_delta"] == 0


def test_receipt_is_bound_to_merged_parent_and_active_peer_repair():
    data = load(RECEIPT)
    assert data["source_parent_pr"] == "GBOGEB/CODEX#330"
    assert data["source_parent_merge_sha"] == "a8525f61102d00cbbe5a7cbe832ac1573a86783c"
    assert data["peer_abacus_pr"] == "GBOGEB/ABACUS#796"
    assert data["peer_abacus_predecessor_pr"] == "GBOGEB/ABACUS#795"


def test_incomplete_runtime_hash_binding_fails_closed():
    data = load(RECEIPT)
    binding = data["runtime_binding"]
    assert binding["complete"] is False
    assert binding["runtime_artifact_sha256"] is None
    assert binding["semantic_result_sha256"] is None
    assert binding["release_manifest_sha256"] is None
    assert data["handoff_gate"]["state"] == "CLOSED"


def test_semantic_request_tracks_current_abacus_repair_lineage():
    request = load(REQUEST)
    assert request["source_abacus_pr"] == "GBOGEB/ABACUS#796"
    assert request["source_abacus_predecessor_pr"] == "GBOGEB/ABACUS#795"
