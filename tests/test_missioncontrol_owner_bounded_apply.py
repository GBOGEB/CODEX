from pathlib import Path

import pytest

from scripts.missioncontrol_bounded_apply import (
    ALLOWED_CHANGED_PATHS,
    GatewayError,
    expected_idempotency_key,
    validate_apply_request,
)
from scripts.missioncontrol_owner_bounded_apply_request import (
    CHANGED_PATHS,
    INTENT,
    OwnerApplyError,
    build_request,
    parse_command,
    sha256_text,
)


SHA = "a" * 40


def request(**overrides):
    value = build_request(
        comment=f"/missioncontrol apply refresh-federation-heads {SHA}",
        observed_head_sha=SHA,
        run_id="12345",
        actor="GBOGEB",
        created_at="2026-09-30T18:00:00+00:00",
    )
    value.update(overrides)
    return value


def test_parse_exact_owner_bounded_apply_command() -> None:
    assert parse_command(
        f"/missioncontrol apply refresh-federation-heads {SHA}"
    ) == SHA


def test_rejects_non_exact_bounded_apply_command() -> None:
    with pytest.raises(OwnerApplyError, match="40-char-main-sha"):
        parse_command("/missioncontrol apply refresh-federation-heads main")


def test_request_binds_apply_class_head_digest_and_allowlist() -> None:
    value = request()
    digest = sha256_text(INTENT)
    assert value["action_class"] == "APPLY_BOUNDED_CODEX"
    assert value["target"]["repo"] == "GBOGEB/CODEX"
    assert value["target"]["ref"] == "main"
    assert value["target"]["expected_head_sha"] == SHA
    assert value["payload_sha256"] == digest
    assert value["idempotency_key"] == f"mc:apply:{SHA}:{digest}"
    assert set(value["changed_paths"]) == ALLOWED_CHANGED_PATHS == set(CHANGED_PATHS)
    assert value["authority_transfer"] is False
    assert value["formal_credit_delta"] == 0
    assert value["engineering_credit_delta"] == 0


def test_validate_bounded_apply_request() -> None:
    assert validate_apply_request(
        request(),
        expected_sha=SHA,
        actor="GBOGEB",
    ) == INTENT


def test_stale_head_fails_closed() -> None:
    with pytest.raises(GatewayError, match="stale target head"):
        validate_apply_request(
            request(),
            expected_sha="b" * 40,
            actor="GBOGEB",
        )


def test_remote_repository_is_rejected() -> None:
    value = request()
    value["target"]["repo"] = "GBOGEB/ABACUS"
    with pytest.raises(GatewayError, match="CODEX-only"):
        validate_apply_request(value, expected_sha=SHA, actor="GBOGEB")


def test_changed_path_allowlist_is_exact() -> None:
    value = request()
    value["changed_paths"] = value["changed_paths"][:-1]
    with pytest.raises(GatewayError, match="changed_paths"):
        validate_apply_request(value, expected_sha=SHA, actor="GBOGEB")


def test_apply_idempotency_key_is_distinct_from_stage_only() -> None:
    digest = sha256_text(INTENT)
    assert expected_idempotency_key(SHA, digest) == f"mc:apply:{SHA}:{digest}"
    assert expected_idempotency_key(SHA, digest) != f"mc:{SHA}:{digest}"


def test_owner_bounded_apply_workflow_is_pr_only() -> None:
    workflow = Path(
        ".github/workflows/missioncontrol-owner-bounded-apply.yml"
    ).read_text(encoding="utf-8")
    assert "github.event.issue.number == 879" in workflow
    assert "github.event.comment.author_association == 'OWNER'" in workflow
    assert "/missioncontrol apply refresh-federation-heads " in workflow
    assert "contents: write" in workflow
    assert "pull-requests: write" in workflow
    assert "gh pr create" in workflow
    assert "git push -u origin" in workflow
    assert "direct_main_write=false" in workflow
    assert "remote_authority_mutation=false" in workflow
    assert "git push origin main" not in workflow
    assert "git push origin HEAD:main" not in workflow
    assert "cancel-in-progress: false" in workflow
