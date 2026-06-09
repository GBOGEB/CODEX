from __future__ import annotations

import copy
import json
from pathlib import Path

from tools.contracts.lineage_validator import validate_payload


def _payload() -> dict:
    return json.loads(Path("generated/lineage.json").read_text(encoding="utf-8"))


def test_lineage_schema_accepts_valid_lineage() -> None:
    errors = validate_payload(_payload())

    assert errors == []


def test_lineage_schema_rejects_invalid_uuid() -> None:
    payload = _payload()
    payload["nodes"][0]["id"] = "not-a-uuid"

    errors = validate_payload(payload)

    assert any(error["code"] == "schema_validation" and "uuid" in error["message"].lower() for error in errors)


def test_lineage_schema_rejects_missing_required_field() -> None:
    payload = _payload()
    del payload["nodes"][0]["created"]

    errors = validate_payload(payload)

    assert any(error["code"] == "schema_validation" and "'created' is a required property" in error["message"] for error in errors)


def test_lineage_schema_rejects_invalid_stage() -> None:
    payload = _payload()
    payload["nodes"][0]["stage"] = "Invalid Stage"

    errors = validate_payload(payload)

    assert any(error["code"] == "schema_validation" and "Invalid Stage" in error["message"] for error in errors)


def test_lineage_schema_rejects_invalid_status() -> None:
    payload = _payload()
    payload["nodes"][0]["status"] = "not-a-status"

    errors = validate_payload(payload)

    assert any(error["code"] == "schema_validation" and "not-a-status" in error["message"] for error in errors)


def test_lineage_schema_detects_broken_references() -> None:
    payload = copy.deepcopy(_payload())
    payload["nodes"][1]["parent"] = "00000000-0000-4000-8000-000000000000"
    payload["traversal"].append("00000000-0000-4000-8000-000000000001")

    errors = validate_payload(payload)

    assert sum(1 for error in errors if error["code"] == "broken_reference") == 2
