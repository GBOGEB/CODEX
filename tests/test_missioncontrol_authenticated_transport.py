import hashlib

import pytest

from scripts.missioncontrol_authenticated_transport import (
    GatewayError,
    build_receipt,
    expected_idempotency_key,
    validate_request,
)


SHA = "a" * 40
INTENT = "REFRESH_FEDERATION_HEADS"
PAYLOAD_SHA = hashlib.sha256(INTENT.encode("utf-8")).hexdigest()


def request(**overrides):
    payload = {
        "schema_version": "0.1",
        "request_id": "mc-test-request-0001",
        "created_at": "2026-09-30T12:00:00Z",
        "requested_by_hint": "browser hint only",
        "target": {
            "repo": "GBOGEB/CODEX",
            "ref": "main",
            "expected_head_sha": SHA,
        },
        "action_class": "STAGE_ONLY",
        "intent": INTENT,
        "payload_sha256": PAYLOAD_SHA,
        "idempotency_key": expected_idempotency_key(SHA, PAYLOAD_SHA),
        "evidence_refs": [
            "mission_control/mycelium/execution_gateway_contract.yaml"
        ],
        "authority_transfer": False,
        "formal_credit_delta": 0,
        "engineering_credit_delta": 0,
    }
    payload.update(overrides)
    return payload


def test_valid_authenticated_transport_request():
    assert (
        validate_request(
            request(),
            expected_sha=SHA,
            actor="GBOGEB",
        )
        == INTENT
    )


def test_stale_head_fails_closed():
    with pytest.raises(GatewayError, match="stale target head"):
        validate_request(
            request(),
            expected_sha="b" * 40,
            actor="GBOGEB",
        )


def test_remote_repository_is_rejected():
    value = request()
    value["target"]["repo"] = "GBOGEB/ABACUS"
    with pytest.raises(GatewayError, match="CODEX-only"):
        validate_request(value, expected_sha=SHA, actor="GBOGEB")


def test_mutation_action_class_is_not_enabled():
    with pytest.raises(GatewayError, match="STAGE_ONLY"):
        validate_request(
            request(action_class="APPLY_BOUNDED_CODEX"),
            expected_sha=SHA,
            actor="GBOGEB",
        )


def test_payload_digest_is_bound_to_intent():
    with pytest.raises(GatewayError, match="payload_sha256"):
        validate_request(
            request(payload_sha256="b" * 64),
            expected_sha=SHA,
            actor="GBOGEB",
        )


def test_idempotency_key_binds_head_and_payload():
    with pytest.raises(GatewayError, match="idempotency_key"):
        validate_request(
            request(idempotency_key="not-the-governed-key"),
            expected_sha=SHA,
            actor="GBOGEB",
        )


def test_receipt_conforms_to_design_schema():
    value = request()
    receipt = build_receipt(
        request=value,
        actor="GBOGEB",
        actor_id="202350393",
        observed_sha=SHA,
        run_id=12345,
        job_id=67890,
    )
    assert receipt["decision"] == "EXECUTED"
    assert receipt["observed_head_sha"] == SHA
    assert receipt["after_sha"] is None
    assert receipt["workflow_run"] == 12345
    assert receipt["workflow_job"] == 67890
    assert receipt["authority_transfer"] is False
    assert receipt["formal_credit_delta"] == 0
    assert receipt["engineering_credit_delta"] == 0


def test_selected_transport_does_not_enable_apply():
    import yaml
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    contract = yaml.safe_load(
        (root / "mission_control/mycelium/execution_gateway_contract.yaml").read_text()
    )
    assert contract["state"] == "BOUNDED_APPLY_IMPLEMENTED_DISABLED_EXACT_HEAD_GREEN"
    assert contract["authentication"]["selected_transport"] == "GITHUB_ACTIONS_WORKFLOW_DISPATCH"
    assert contract["authentication"]["enabled_mutation_transports"] == []
    assert contract["authorization"]["action_classes"]["APPLY_BOUNDED_CODEX"]["enabled"] is False
    assert contract["transport_runtime"]["mutation_enabled"] is False
    assert contract["bounded_apply_runtime"]["mutation_enabled"] is False
    assert contract["bounded_apply_runtime"]["execute_permitted"] is False
    assert contract["bounded_apply_runtime"]["enabled_mutation_transports"] == []
    assert contract["promotion"]["mutation_promotion_state"] == "WITHHELD_EXPLICIT_PROMOTION_REQUIRED"
