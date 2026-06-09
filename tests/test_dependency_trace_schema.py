from __future__ import annotations

import copy
import json
from pathlib import Path

from tools.contracts.dependency_trace_validator import validate_payload


def _payload() -> dict:
    return json.loads(Path("generated/trace_matrix.json").read_text(encoding="utf-8"))


def test_dependency_trace_schema_accepts_valid_trace() -> None:
    errors = validate_payload(_payload())

    assert errors == []


def test_dependency_trace_schema_rejects_invalid_uuid() -> None:
    payload = _payload()
    payload["nodes"][0]["id"] = "not-a-uuid"

    errors = validate_payload(payload)

    assert any(error["code"] == "schema_validation" and "uuid" in error["message"].lower() for error in errors)


def test_dependency_trace_schema_rejects_missing_required_field() -> None:
    payload = _payload()
    del payload["nodes"][0]["title"]

    errors = validate_payload(payload)

    assert any(error["code"] == "schema_validation" and "'title' is a required property" in error["message"] for error in errors)


def test_dependency_trace_schema_rejects_invalid_stage() -> None:
    payload = _payload()
    payload["nodes"][0]["stage"] = "Invalid Stage"

    errors = validate_payload(payload)

    assert any(error["code"] == "schema_validation" and "Invalid Stage" in error["message"] for error in errors)


def test_dependency_trace_schema_detects_broken_parent_reference() -> None:
    payload = _payload()
    payload = copy.deepcopy(payload)
    payload["nodes"][1]["parent"] = "00000000-0000-4000-8000-000000000000"

    errors = validate_payload(payload)

    assert any(error["code"] == "broken_reference" for error in errors)
