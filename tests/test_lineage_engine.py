from __future__ import annotations

from tools.traceability.lineage_engine import (
    DEFAULT_CREATED,
    DEFAULT_UPDATED,
    default_lineage_nodes,
    traverse_lineage,
    validate_lineage_nodes,
)
from tools.traceability.trace_models import LineageNode, LineageStage, stable_uuid


def _lineage_node(
    node_id: str,
    stage: LineageStage,
    title: str,
    parent: str | None,
) -> LineageNode:
    return LineageNode(
        id=node_id,
        stage=stage,
        title=title,
        created=DEFAULT_CREATED,
        updated=DEFAULT_UPDATED,
        parent=parent,
        status="planned",
    )


def test_lineage_engine_accepts_valid_chain() -> None:
    nodes = default_lineage_nodes()
    result = validate_lineage_nodes(nodes)

    assert result["status"] == "pass"
    assert result["error_count"] == 0
    assert result["traversal"] == [node.id for node in nodes]


def test_lineage_traversal_returns_complete_required_path() -> None:
    nodes = default_lineage_nodes()

    traversal = traverse_lineage(nodes)

    assert traversal == [node.id for node in nodes]


def test_lineage_engine_detects_broken_parent() -> None:
    node = _lineage_node(
        stable_uuid("test/lineage/orphan-review"),
        LineageStage.REVIEW,
        "Review with missing parent",
        stable_uuid("test/lineage/missing-applicant-package"),
    )

    result = validate_lineage_nodes([node])

    assert result["status"] == "fail"
    assert any(error["code"] == "broken_lineage_chain" for error in result["errors"])
    assert any(error["code"] == "incomplete_lineage_traversal" for error in result["errors"])


def test_lineage_engine_detects_duplicate_ids() -> None:
    duplicate_id = stable_uuid("test/lineage/duplicate")
    nodes = [
        _lineage_node(duplicate_id, LineageStage.ITT, "ITT one", None),
        _lineage_node(duplicate_id, LineageStage.ITT, "ITT two", None),
    ]

    result = validate_lineage_nodes(nodes)

    assert result["status"] == "fail"
    assert any(error["code"] == "duplicate_lineage_id" for error in result["errors"])


def test_lineage_engine_detects_cycle() -> None:
    itt_id = stable_uuid("test/lineage/cycle-itt")
    applicant_id = stable_uuid("test/lineage/cycle-applicant")
    review_id = stable_uuid("test/lineage/cycle-review")
    nodes = [
        _lineage_node(itt_id, LineageStage.ITT, "ITT in cycle", review_id),
        _lineage_node(applicant_id, LineageStage.APPLICANT_PACKAGE, "Applicant in cycle", itt_id),
        _lineage_node(review_id, LineageStage.REVIEW, "Review in cycle", applicant_id),
    ]

    result = validate_lineage_nodes(nodes)

    assert result["status"] == "fail"
    assert any(error["code"] == "cyclic_lineage" for error in result["errors"])
