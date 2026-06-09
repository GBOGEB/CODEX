"""Validate and report the W002 governance lineage chain.

Required lineage:
ITT → Applicant Package → Review → Revision → Approval → Baseline.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.traceability.lineage_report import generate_reports
from tools.traceability.trace_models import (
    LINEAGE_STAGE_ORDER,
    LineageNode,
    LineageStage,
    ValidationIssue,
    is_uuid,
    stable_uuid,
    utc_now,
)

DEFAULT_LINEAGE_INPUT_PATH = Path("MASTER_input/Traceability/lineage.json")
DEFAULT_CREATED = "2026-06-09T00:00:00+00:00"
DEFAULT_UPDATED = "2026-06-09T00:00:00+00:00"

_STAGE_INDEX = {stage: index for index, stage in enumerate(LINEAGE_STAGE_ORDER)}


def default_lineage_nodes() -> list[LineageNode]:
    """Return a minimal valid repository-seeded lineage chain for W002."""
    itt = stable_uuid("lineage/itt")
    applicant_package = stable_uuid("lineage/applicant-package")
    review = stable_uuid("lineage/review")
    revision = stable_uuid("lineage/revision")
    approval = stable_uuid("lineage/approval")
    baseline = stable_uuid("lineage/baseline")
    return [
        LineageNode(
            id=itt,
            stage=LineageStage.ITT,
            title="Issued ITT governance package",
            created=DEFAULT_CREATED,
            updated=DEFAULT_UPDATED,
            parent=None,
            status="complete",
        ),
        LineageNode(
            id=applicant_package,
            stage=LineageStage.APPLICANT_PACKAGE,
            title="Applicant package placeholder",
            created=DEFAULT_CREATED,
            updated=DEFAULT_UPDATED,
            parent=itt,
            status="active",
        ),
        LineageNode(
            id=review,
            stage=LineageStage.REVIEW,
            title="Review package placeholder",
            created=DEFAULT_CREATED,
            updated=DEFAULT_UPDATED,
            parent=applicant_package,
            status="planned",
        ),
        LineageNode(
            id=revision,
            stage=LineageStage.REVISION,
            title="Revision package placeholder",
            created=DEFAULT_CREATED,
            updated=DEFAULT_UPDATED,
            parent=review,
            status="planned",
        ),
        LineageNode(
            id=approval,
            stage=LineageStage.APPROVAL,
            title="Approval package placeholder",
            created=DEFAULT_CREATED,
            updated=DEFAULT_UPDATED,
            parent=revision,
            status="planned",
        ),
        LineageNode(
            id=baseline,
            stage=LineageStage.BASELINE,
            title="Baseline package placeholder",
            created=DEFAULT_CREATED,
            updated=DEFAULT_UPDATED,
            parent=approval,
            status="planned",
        ),
    ]


def load_lineage_nodes(input_path: Path | str = DEFAULT_LINEAGE_INPUT_PATH) -> list[LineageNode]:
    """Load lineage nodes from JSON if present; otherwise use the seeded valid chain."""
    path = Path(input_path)
    if not path.exists():
        return default_lineage_nodes()

    payload = json.loads(path.read_text(encoding="utf-8"))
    records = payload["nodes"] if isinstance(payload, dict) and "nodes" in payload else payload
    if not isinstance(records, list):
        raise TypeError(f"Lineage input must be a list or an object with a nodes list: {path}")
    return [LineageNode.from_mapping(record) for record in records]


def _cycle_issues(nodes_by_id: dict[str, LineageNode]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: LineageNode, trail: list[str]) -> None:
        if node.id in visited:
            return
        if node.id in visiting:
            cycle = " -> ".join([*trail, node.id])
            issues.append(ValidationIssue("cyclic_lineage", f"Cyclic lineage detected: {cycle}", node.id))
            return
        visiting.add(node.id)
        if node.parent and node.parent in nodes_by_id:
            visit(nodes_by_id[node.parent], [*trail, node.id])
        visiting.remove(node.id)
        visited.add(node.id)

    for node in nodes_by_id.values():
        visit(node, [])
    return issues


def traverse_lineage(nodes: list[LineageNode]) -> list[str]:
    """Return the first complete lineage traversal in required stage order."""
    by_parent: dict[str | None, list[LineageNode]] = {}
    for node in nodes:
        by_parent.setdefault(node.parent, []).append(node)

    roots = [node for node in by_parent.get(None, []) if node.stage is LineageStage.ITT]
    for root in roots:
        traversal = [root]
        current = root
        for expected_stage in LINEAGE_STAGE_ORDER[1:]:
            candidates = [node for node in by_parent.get(current.id, []) if node.stage is expected_stage]
            if not candidates:
                break
            current = sorted(candidates, key=lambda node: node.id)[0]
            traversal.append(current)
        if [node.stage for node in traversal] == list(LINEAGE_STAGE_ORDER):
            return [node.id for node in traversal]
    return []


def validate_lineage_nodes(nodes: list[LineageNode]) -> dict[str, Any]:
    """Validate lineage nodes and return a report dictionary."""
    errors: list[ValidationIssue] = []
    counts = Counter(node.id for node in nodes)
    for node_id, count in sorted(counts.items()):
        if count > 1:
            errors.append(ValidationIssue("duplicate_lineage_id", f"Duplicate lineage ID detected: {node_id}", node_id))

    for node in nodes:
        if not is_uuid(node.id):
            errors.append(ValidationIssue("invalid_lineage_id", f"Lineage ID is not a valid UUID: {node.id}", node.id))
        for field_name in ("created", "updated", "status"):
            if not getattr(node, field_name):
                errors.append(
                    ValidationIssue(
                        "missing_lineage_field",
                        f"Lineage node is missing required field: {field_name}",
                        node.id,
                    )
                )

    nodes_by_id: dict[str, LineageNode] = {}
    for node in nodes:
        nodes_by_id.setdefault(node.id, node)

    for node in nodes:
        if node.stage is LineageStage.ITT:
            if node.parent is not None:
                errors.append(
                    ValidationIssue("broken_lineage_chain", "ITT must start the lineage chain without a parent.", node.id)
                )
            continue

        if node.parent is None or node.parent not in nodes_by_id:
            errors.append(
                ValidationIssue("broken_lineage_chain", f"{node.stage.value} parent is missing or unknown.", node.id)
            )
            continue

        expected_parent_stage = LINEAGE_STAGE_ORDER[_STAGE_INDEX[node.stage] - 1]
        parent = nodes_by_id[node.parent]
        if parent.stage is not expected_parent_stage:
            errors.append(
                ValidationIssue(
                    "broken_lineage_chain",
                    f"{node.stage.value} must link from {expected_parent_stage.value}, not {parent.stage.value}.",
                    node.id,
                )
            )

    errors.extend(_cycle_issues(nodes_by_id))
    traversal = traverse_lineage(nodes)
    if not traversal:
        errors.append(
            ValidationIssue(
                "incomplete_lineage_traversal",
                "No complete ITT → Applicant Package → Review → Revision → Approval → Baseline traversal found.",
            )
        )

    error_payloads = [issue.as_dict() for issue in errors]
    return {
        "status": "pass" if not error_payloads else "fail",
        "checked_at": utc_now(),
        "model": [stage.value for stage in LINEAGE_STAGE_ORDER],
        "node_count": len(nodes),
        "error_count": len(error_payloads),
        "errors": error_payloads,
        "traversal": traversal,
        "nodes": [node.as_dict() for node in nodes],
    }


def main() -> int:
    """CLI entrypoint. Returns non-zero when lineage validation fails."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_LINEAGE_INPUT_PATH)
    parser.add_argument("--json-report", type=Path, default=Path("generated/lineage.json"))
    parser.add_argument("--markdown-report", type=Path, default=Path("generated/lineage.md"))
    parser.add_argument("--graph-report", type=Path, default=Path("generated/lineage_graph.json"))
    args = parser.parse_args()

    nodes = load_lineage_nodes(args.input)
    report = validate_lineage_nodes(nodes)
    generate_reports(report, args.json_report, args.markdown_report, args.graph_report)

    if report["status"] == "fail":
        print(f"Lineage validation failed with {report['error_count']} error(s).")
        for error in report["errors"]:
            print(f"- {error['code']}: {error['message']}")
        return 1

    print("Lineage validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
