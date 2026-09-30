import copy

import pytest

from scripts.missioncontrol_bounded_apply import (
    BoundedApplyError,
    expected_idempotency_key,
    expected_payload_sha256,
    validate_bounded_apply,
)


SHA = "a" * 40
DRY_RECEIPT_REF = (
    "mission_control/mycelium/gateway/receipts/"
    "missioncontrol-stage-only-test-12345-1.json"
)


def policy() -> dict:
    return {
        "policy_id": "MISSIONCONTROL_CODEX_BOUNDED_APPLY_V0_1",
        "mutation_enabled": False,
        "enabled_mutation_transports": [],
        "target": {"repository": "GBOGEB/CODEX", "ref": "main"},
        "allowed_intents": ["CONTROLLED_CODEX_CONTROL_PLANE_UPDATE"],
        "changed_path_allowlist": [
            "mission_control/mycelium/control_plane_projection.json",
            "docs/data/missioncontrol_control_plane.json",
        ],
        "approval": {
            "accepted_ref_prefix": "https://github.com/GBOGEB/CODEX/issues/"
        },
        "dry_run": {"required_decision": "EXECUTED"},
    }


def dry_receipt(**overrides) -> dict:
    value = {
        "decision": "EXECUTED",
        "observed_head_sha": SHA,
        "after_sha": None,
        "authority_transfer": False,
        "formal_credit_delta": 0,
        "engineering_credit_delta": 0,
    }
    value.update(overrides)
    return value


def request(**overrides) -> dict:
    value = {
        "schema_version": "0.1",
        "request_id": "mc-bounded-apply-test-0001",
        "created_at": "2026-09-30T18:20:00Z",
        "requested_by_hint": "untrusted browser hint",
        "target": {
            "repo": "GBOGEB/CODEX",
            "ref": "main",
            "expected_head_sha": SHA,
        },
        "action_class": "APPLY_BOUNDED_CODEX",
        "intent": "CONTROLLED_CODEX_CONTROL_PLANE_UPDATE",
        "changed_paths": [
            "mission_control/mycelium/control_plane_projection.json"
        ],
        "approval_ref": "https://github.com/GBOGEB/CODEX/issues/879#issuecomment-test",
        "dry_run_receipt_ref": DRY_RECEIPT_REF,
        "payload_sha256": "0" * 64,
        "idempotency_key": "placeholder-key",
        "evidence_refs": [
            "mission_control/mycelium/bounded_apply_policy.yaml"
        ],
        "authority_transfer": False,
        "formal_credit_delta": 0,
        "engineering_credit_delta": 0,
    }
    for key, val in overrides.items():
        if key == "target":
            value["target"] = val
        else:
            value[key] = val
    digest = expected_payload_sha256(value)
    value["payload_sha256"] = digest
    value["idempotency_key"] = expected_idempotency_key(
        value["target"]["expected_head_sha"], digest
    )
    return value


def validate(value: dict, *, receipt: dict | None = None, completed=None):
    return validate_bounded_apply(
        value,
        observed_head_sha=SHA,
        actor="GBOGEB",
        policy=policy(),
        dry_run_receipt=receipt or dry_receipt(),
        completed_idempotency_keys=set(completed or []),
    )


def test_valid_bounded_apply_plan_is_still_withheld() -> None:
    plan = validate(request())
    assert plan["decision"] == "WITHHELD_MUTATION_DISABLED"
    assert plan["mutation_enabled"] is False
    assert plan["execute_permitted"] is False
    assert plan["enabled_mutation_transports"] == []
    assert plan["authority_transfer"] is False
    assert plan["formal_credit_delta"] == 0
    assert plan["engineering_credit_delta"] == 0


def test_remote_repository_is_rejected() -> None:
    value = request()
    value["target"] = dict(value["target"], repo="GBOGEB/ABACUS")
    digest = expected_payload_sha256(value)
    value["payload_sha256"] = digest
    value["idempotency_key"] = expected_idempotency_key(SHA, digest)
    with pytest.raises(BoundedApplyError, match="GBOGEB/CODEX"):
        validate(value)


def test_stale_head_is_rejected() -> None:
    value = request()
    with pytest.raises(BoundedApplyError, match="stale target head"):
        validate_bounded_apply(
            value,
            observed_head_sha="b" * 40,
            actor="GBOGEB",
            policy=policy(),
            dry_run_receipt=dry_receipt(),
            completed_idempotency_keys=set(),
        )


def test_disallowed_changed_path_is_rejected() -> None:
    value = request(changed_paths=[".github/workflows/ci.yml"])
    with pytest.raises(BoundedApplyError, match="outside bounded CODEX allowlist"):
        validate(value)


def test_missing_explicit_approval_is_rejected() -> None:
    value = request(approval_ref="")
    with pytest.raises(BoundedApplyError, match="approval_ref"):
        validate(value)


def test_dry_run_must_bind_same_exact_head_and_no_mutation() -> None:
    with pytest.raises(BoundedApplyError, match="same exact head|requested exact head"):
        validate(request(), receipt=dry_receipt(observed_head_sha="b" * 40))
    with pytest.raises(BoundedApplyError, match="prove no mutation"):
        validate(request(), receipt=dry_receipt(after_sha="b" * 40))


def test_completed_idempotency_key_replay_is_rejected() -> None:
    value = request()
    with pytest.raises(BoundedApplyError, match="replay is forbidden"):
        validate(value, completed={value["idempotency_key"]})


def test_payload_digest_covers_changed_paths_and_approval() -> None:
    base = request()
    altered = copy.deepcopy(base)
    altered["changed_paths"] = ["docs/data/missioncontrol_control_plane.json"]
    assert expected_payload_sha256(altered) != base["payload_sha256"]
    altered = copy.deepcopy(base)
    altered["approval_ref"] += "-different"
    assert expected_payload_sha256(altered) != base["payload_sha256"]
