from __future__ import annotations

from scripts.check_pages_source_mode import inspect_pages_site


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
