from __future__ import annotations

from scripts.check_pages_source_mode import build_receipt, inspect_pages_site


def test_workflow_source_mode_passes() -> None:
    payload = {"build_type": "workflow", "source": None}
    assert inspect_pages_site(payload) == []


def test_legacy_branch_source_fails_closed() -> None:
    payload = {
        "build_type": "legacy",
        "source": {"branch": "main", "path": "/docs"},
    }
    errors = inspect_pages_site(payload)
    assert errors
    assert "build_type='legacy'" in errors[0]
    assert "main:/docs" in errors[0]


def test_missing_build_type_fails_closed() -> None:
    errors = inspect_pages_site({"source": {"branch": "main", "path": "/docs"}})
    assert errors
    assert "required='workflow'" in errors[0]


def test_non_object_payload_fails_closed() -> None:
    assert inspect_pages_site([]) == ["Pages site response is not a JSON object"]


def test_legacy_receipt_is_lossless_and_zero_credit(monkeypatch) -> None:
    monkeypatch.setenv("GITHUB_SHA", "abc123")
    monkeypatch.setenv("GITHUB_RUN_ID", "42")
    monkeypatch.setenv("GITHUB_RUN_ATTEMPT", "2")
    payload = {
        "build_type": "legacy",
        "source": {"branch": "main", "path": "/docs"},
    }
    errors = inspect_pages_site(payload)

    receipt = build_receipt("GBOGEB/CODEX", payload, errors)

    assert receipt["status"] == "FAIL"
    assert receipt["observed_build_type"] == "legacy"
    assert receipt["observed_source_branch"] == "main"
    assert receipt["observed_source_path"] == "/docs"
    assert receipt["source_sha"] == "abc123"
    assert receipt["run_id"] == "42"
    assert receipt["run_attempt"] == "2"
    assert receipt["owner_action_required"] is True
    assert receipt["formal_credit_delta"] == 0
    assert receipt["authority_transfer"] is False


def test_workflow_receipt_clears_owner_action() -> None:
    payload = {"build_type": "workflow", "source": None}
    receipt = build_receipt("GBOGEB/CODEX", payload, [])

    assert receipt["status"] == "PASS"
    assert receipt["owner_action_required"] is False
    assert receipt["owner_action"] is None
    assert receipt["reentry"] is None
    assert receipt["formal_credit_delta"] == 0
    assert receipt["authority_transfer"] is False
