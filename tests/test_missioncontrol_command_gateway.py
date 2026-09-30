import pytest

from scripts.missioncontrol_command_gateway import GatewayError, validate_envelope


SHA = "a" * 40


def envelope(**overrides):
    payload = {
        "schema_version": "0.2.1",
        "event_type": "USER_STEER",
        "requested_mode": "APPLY",
        "effective_mode": "STAGED_APPLY_WITHHELD_NO_AUTHENTICATED_GATEWAY",
        "repository": "GBOGEB/CODEX",
        "lane": "FEDERATION",
        "source_authority_sha": SHA,
        "command_format": "JSON",
        "command": {"action": "REFRESH_FEDERATION_HEADS"},
        "parse_ok": True,
        "invariants": {
            "authority_transfer": False,
            "formal_credit_delta": 0,
            "engineering_credit_delta": 0,
            "replay_completed_atoms": False,
        },
    }
    payload.update(overrides)
    return payload


def test_valid_authenticated_envelope_is_allowlisted():
    assert validate_envelope(envelope(), expected_sha=SHA, actor="gbo") == "REFRESH_FEDERATION_HEADS"


def test_stale_source_sha_fails_closed():
    with pytest.raises(GatewayError, match="stale source authority"):
        validate_envelope(envelope(), expected_sha="b" * 40, actor="gbo")


def test_authority_transfer_request_is_rejected():
    payload = envelope()
    payload["invariants"]["authority_transfer"] = True
    with pytest.raises(GatewayError, match="authority_transfer"):
        validate_envelope(payload, expected_sha=SHA, actor="gbo")


def test_unknown_action_is_rejected():
    payload = envelope(command={"action": "DELETE_REPOSITORY"})
    with pytest.raises(GatewayError, match="not allow-listed"):
        validate_envelope(payload, expected_sha=SHA, actor="gbo")


def test_remote_target_repository_is_rejected():
    payload = envelope(repository="GBOGEB/ABACUS")
    with pytest.raises(GatewayError, match="target repository"):
        validate_envelope(payload, expected_sha=SHA, actor="gbo")


def test_missing_actor_is_rejected():
    with pytest.raises(GatewayError, match="actor"):
        validate_envelope(envelope(), expected_sha=SHA, actor="")
