from scripts.missioncontrol_owner_comment_request import (
    OwnerCommentError,
    build_request,
    parse_command,
    sha256_text,
)


SHA = "a" * 40


def test_parse_exact_owner_command() -> None:
    assert parse_command(
        f"/missioncontrol stage refresh-federation-heads {SHA}"
    ) == SHA


def test_rejects_non_exact_command() -> None:
    try:
        parse_command("/missioncontrol stage refresh-federation-heads main")
    except OwnerCommentError as exc:
        assert "40-char-main-sha" in str(exc)
    else:
        raise AssertionError("invalid owner command was accepted")


def test_build_request_binds_exact_head_and_no_mutation() -> None:
    request = build_request(
        comment=f"/missioncontrol stage refresh-federation-heads {SHA}",
        observed_head_sha=SHA,
        run_id="12345",
        actor="GBOGEB",
        created_at="2026-09-30T16:55:00+00:00",
    )
    assert request["action_class"] == "STAGE_ONLY"
    assert request["intent"] == "REFRESH_FEDERATION_HEADS"
    assert request["target"]["expected_head_sha"] == SHA
    assert request["payload_sha256"] == sha256_text("REFRESH_FEDERATION_HEADS")
    assert request["idempotency_key"] == (
        f"mc:{SHA}:{sha256_text('REFRESH_FEDERATION_HEADS')}"
    )
    assert request["authority_transfer"] is False
    assert request["formal_credit_delta"] == 0
    assert request["engineering_credit_delta"] == 0
    assert "changed_paths" not in request


def test_rejects_stale_owner_command() -> None:
    try:
        build_request(
            comment=f"/missioncontrol stage refresh-federation-heads {SHA}",
            observed_head_sha="b" * 40,
            run_id="12345",
            actor="GBOGEB",
        )
    except OwnerCommentError as exc:
        assert "stale owner command" in str(exc)
    else:
        raise AssertionError("stale owner command was accepted")
