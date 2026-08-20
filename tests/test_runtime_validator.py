from __future__ import annotations

import copy

from tools.contracts.runtime_validator import validate_payload
from tools.export.governance_export import build_governance_runtime


def test_runtime_validator_accepts_valid_runtime() -> None:
    errors = validate_payload(build_governance_runtime())

    assert errors == []


def test_runtime_validator_rejects_invalid_runtime_uuid() -> None:
    runtime = build_governance_runtime()
    runtime["runtime_id"] = "not-a-uuid"

    errors = validate_payload(runtime)

    assert any(error["code"] == "schema_validation" and "uuid" in error["message"].lower() for error in errors)


def test_runtime_validator_rejects_missing_required_section() -> None:
    runtime = build_governance_runtime()
    del runtime["validation_reports"]

    errors = validate_payload(runtime)

    assert any(
        error["code"] == "schema_validation" and "'validation_reports' is a required property" in error["message"]
        for error in errors
    )


def test_runtime_validator_rejects_invalid_dependency_stage() -> None:
    runtime = build_governance_runtime()
    runtime["dependency_trace"]["nodes"][0]["stage"] = "Invalid Stage"

    errors = validate_payload(runtime)

    assert any(error["code"] == "schema_validation" and "Invalid Stage" in error["message"] for error in errors)


def test_runtime_validator_rejects_invalid_lineage_status() -> None:
    runtime = build_governance_runtime()
    runtime["lineage_trace"]["nodes"][0]["status"] = "not-a-status"

    errors = validate_payload(runtime)

    assert any(error["code"] == "schema_validation" and "not-a-status" in error["message"] for error in errors)


def test_runtime_validator_detects_broken_references() -> None:
    runtime = copy.deepcopy(build_governance_runtime())
    runtime["dependency_trace"]["links"][0]["target"] = "00000000-0000-4000-8000-000000000000"
    runtime["lineage_trace"]["traversal"].append("00000000-0000-4000-8000-000000000001")

    errors = validate_payload(runtime)

    assert sum(1 for error in errors if error["code"] == "broken_reference") == 2
