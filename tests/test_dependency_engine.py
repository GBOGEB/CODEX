from __future__ import annotations

from tools.traceability.dependency_engine import default_trace_nodes, validate_trace_nodes
from tools.traceability.trace_models import TraceNode, TraceStage, stable_uuid


def test_dependency_engine_accepts_valid_chain() -> None:
    result = validate_trace_nodes(default_trace_nodes())

    assert result["status"] == "pass"
    assert result["error_count"] == 0
    assert result["model"] == [
        "Requirement",
        "Applicant Response",
        "Review",
        "Change Request",
        "Approval",
        "Generated Artifact",
    ]


def test_dependency_engine_detects_orphan_requirement() -> None:
    nodes = [
        TraceNode(
            id=stable_uuid("test/orphan-requirement"),
            stage=TraceStage.REQUIREMENT,
            title="Requirement without response",
        )
    ]

    result = validate_trace_nodes(nodes)

    assert result["status"] == "fail"
    assert any(error["code"] == "orphan_requirement" for error in result["errors"])


def test_dependency_engine_detects_orphan_response() -> None:
    nodes = [
        TraceNode(
            id=stable_uuid("test/orphan-response"),
            stage=TraceStage.APPLICANT_RESPONSE,
            title="Response without requirement",
            parent=stable_uuid("test/missing-requirement"),
        )
    ]

    result = validate_trace_nodes(nodes)

    assert result["status"] == "fail"
    assert any(error["code"] == "orphan_response" for error in result["errors"])


def test_dependency_engine_detects_duplicate_trace_ids() -> None:
    duplicate_id = stable_uuid("test/duplicate-trace-id")
    nodes = [
        TraceNode(id=duplicate_id, stage=TraceStage.REQUIREMENT, title="First"),
        TraceNode(id=duplicate_id, stage=TraceStage.REQUIREMENT, title="Second"),
    ]

    result = validate_trace_nodes(nodes)

    assert result["status"] == "fail"
    assert any(error["code"] == "duplicate_trace_id" for error in result["errors"])


def test_dependency_engine_detects_cycle() -> None:
    requirement_id = stable_uuid("test/cycle-requirement")
    response_id = stable_uuid("test/cycle-response")
    review_id = stable_uuid("test/cycle-review")
    nodes = [
        TraceNode(
            id=requirement_id,
            stage=TraceStage.REQUIREMENT,
            title="Requirement in cycle",
            parent=review_id,
        ),
        TraceNode(
            id=response_id,
            stage=TraceStage.APPLICANT_RESPONSE,
            title="Response in cycle",
            parent=requirement_id,
        ),
        TraceNode(
            id=review_id,
            stage=TraceStage.REVIEW,
            title="Review in cycle",
            parent=response_id,
        ),
    ]

    result = validate_trace_nodes(nodes)

    assert result["status"] == "fail"
    assert any(error["code"] == "cyclic_dependency" for error in result["errors"])
