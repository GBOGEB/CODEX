"""Validate and report the W002 dependency trace matrix.

Required chain:
Requirement → Applicant Response → Review → Change Request → Approval → Generated Artifact.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

# Handle both package-relative and direct-script execution
if __name__ == "__main__" and not __package__:
    sys.path.insert(0, str(Path(__file__).parent))
    from trace_models import (
        TRACE_STAGE_ORDER,
        TraceNode,
        TraceStage,
        ValidationIssue,
        is_uuid,
        stable_uuid,
        utc_now,
    )
    from trace_report import generate_reports
else:
    from .trace_models import (
        TRACE_STAGE_ORDER,
        TraceNode,
        TraceStage,
        ValidationIssue,
        is_uuid,
        stable_uuid,
        utc_now,
    )
    from .trace_report import generate_reports

DEFAULT_TRACE_INPUT_PATH = Path("MASTER_input/Traceability/dependency_trace.json")


_STAGE_INDEX = {stage: index for index, stage in enumerate(TRACE_STAGE_ORDER)}


def default_trace_nodes() -> list[TraceNode]:
    """Return a minimal valid repository-seeded trace chain for W002."""
    requirement = stable_uuid("dependency/requirement/itt-governance-baseline")
    response = stable_uuid("dependency/response/applicant-governance-baseline")
    review = stable_uuid("dependency/review/governance-baseline-review")
    change_request = stable_uuid("dependency/change-request/additive-ssot-cr")
    approval = stable_uuid("dependency/approval/w002-governance-approval")
    artifact = stable_uuid("dependency/artifact/generated-trace-matrix")
    return [
        TraceNode(
            id=requirement,
            stage=TraceStage.REQUIREMENT,
            title="ITT governance baseline requirement",
            source_path="ssot/master_contract_ssot_v0_2.yaml",
        ),
        TraceNode(
            id=response,
            stage=TraceStage.APPLICANT_RESPONSE,
            title="Applicant package response placeholder",
            parent=requirement,
            source_path="MASTER_input/06_APPLICANT_RESPONSES/README.md",
        ),
        TraceNode(
            id=review,
            stage=TraceStage.REVIEW,
            title="Governance review placeholder",
            parent=response,
            source_path="MASTER_input/07_EVALUATION/README.md",
        ),
        TraceNode(
            id=change_request,
            stage=TraceStage.CHANGE_REQUEST,
            title="Additive SSOT change request placeholder",
            parent=review,
            source_path="MASTER_input/05_CLARIFICATIONS/README.md",
        ),
        TraceNode(
            id=approval,
            stage=TraceStage.APPROVAL,
            title="W002 traceability approval placeholder",
            parent=change_request,
            source_path="MASTER_input/10_AWARD/README.md",
        ),
        TraceNode(
            id=artifact,
            stage=TraceStage.GENERATED_ARTIFACT,
            title="Generated trace matrix reports",
            parent=approval,
            source_path="generated/trace_matrix.json",
        ),
    ]


def load_trace_nodes(input_path: Path | str = DEFAULT_TRACE_INPUT_PATH) -> list[TraceNode]:
    """Load trace nodes from JSON if present; otherwise use the seeded valid chain."""
    path = Path(input_path)
    if not path.exists():
        return default_trace_nodes()

    payload = json.loads(path.read_text(encoding="utf-8"))
    records = payload["nodes"] if isinstance(payload, dict) and "nodes" in payload else payload
    if not isinstance(records, list):
        raise TypeError(f"Trace input must be a list or an object with a nodes list: {path}")
    return [TraceNode.from_mapping(record) for record in records]


def _duplicate_id_issues(nodes: list[TraceNode]) -> list[ValidationIssue]:
    counts = Counter(node.id for node in nodes)
    return [
        ValidationIssue("duplicate_trace_id", f"Duplicate trace ID detected: {node_id}", node_id)
        for node_id, count in sorted(counts.items())
        if count > 1
    ]


def _uuid_issues(nodes: list[TraceNode]) -> list[ValidationIssue]:
    return [
        ValidationIssue("invalid_trace_id", f"Trace ID is not a valid UUID: {node.id}", node.id)
        for node in nodes
        if not is_uuid(node.id)
    ]


def _children_by_parent(nodes: Iterable[TraceNode]) -> dict[str, list[TraceNode]]:
    children: dict[str, list[TraceNode]] = defaultdict(list)
    for node in nodes:
        if node.parent:
            children[node.parent].append(node)
    return children


def _cycle_issues(nodes_by_id: dict[str, TraceNode]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: TraceNode, trail: list[str]) -> None:
        if node.id in visited:
            return
        if node.id in visiting:
            cycle = " -> ".join([*trail, node.id])
            issues.append(ValidationIssue("cyclic_dependency", f"Cyclic dependency detected: {cycle}", node.id))
            return
        visiting.add(node.id)
        if node.parent and node.parent in nodes_by_id:
            visit(nodes_by_id[node.parent], [*trail, node.id])
        visiting.remove(node.id)
        visited.add(node.id)

    for node in nodes_by_id.values():
        visit(node, [])
    return issues


def validate_trace_nodes(nodes: list[TraceNode]) -> dict[str, Any]:
    """Validate dependency trace nodes and return a report dictionary."""
    errors: list[ValidationIssue] = []
    errors.extend(_duplicate_id_issues(nodes))
    errors.extend(_uuid_issues(nodes))
    for node in nodes:
        for field_name in ("title", "source_path"):
            if not getattr(node, field_name, None):
                errors.append(
                    ValidationIssue(
                        "missing_trace_field",
                        f"Trace node is missing required field: {field_name}",
                        node.id,
                    )
                )
    nodes_by_id: dict[str, TraceNode] = {}
    for node in nodes:
        nodes_by_id.setdefault(node.id, node)

    children = _children_by_parent(nodes)

    for node in nodes:
        if node.stage is TraceStage.REQUIREMENT:
            if node.parent is not None:
                errors.append(
                    ValidationIssue(
                        "broken_trace_chain",
                        "Requirement nodes must start the trace chain and cannot have a parent.",
                        node.id,
                    )
                )
            if not any(child.stage is TraceStage.APPLICANT_RESPONSE for child in children.get(node.id, [])):
                errors.append(
                    ValidationIssue(
                        "orphan_requirement",
                        "Requirement has no Applicant Response child.",
                        node.id,
                    )
                )
            continue

        if node.parent is None or node.parent not in nodes_by_id:
            code = "orphan_response" if node.stage is TraceStage.APPLICANT_RESPONSE else "broken_trace_chain"
            errors.append(ValidationIssue(code, f"{node.stage.value} parent is missing or unknown.", node.id))
            continue

        parent = nodes_by_id[node.parent]
        expected_parent_stage = TRACE_STAGE_ORDER[_STAGE_INDEX[node.stage] - 1]
        if parent.stage is not expected_parent_stage:
            errors.append(
                ValidationIssue(
                    "broken_trace_chain",
                    f"{node.stage.value} must link from {expected_parent_stage.value}, not {parent.stage.value}.",
                    node.id,
                )
            )

        if node.stage is TraceStage.APPLICANT_RESPONSE and parent.stage is not TraceStage.REQUIREMENT:
            errors.append(ValidationIssue("orphan_response", "Applicant Response is not linked to a Requirement.", node.id))

        if node.stage is not TraceStage.GENERATED_ARTIFACT:
            next_stage = TRACE_STAGE_ORDER[_STAGE_INDEX[node.stage] + 1]
            if not any(child.stage is next_stage for child in children.get(node.id, [])):
                errors.append(
                    ValidationIssue(
                        "broken_trace_chain",
                        f"{node.stage.value} has no {next_stage.value} child.",
                        node.id,
                    )
                )

    errors.extend(_cycle_issues(nodes_by_id))
    error_payloads = [issue.as_dict() for issue in errors]
    return {
        "status": "pass" if not error_payloads else "fail",
        "checked_at": utc_now(),
        "model": [stage.value for stage in TRACE_STAGE_ORDER],
        "node_count": len(nodes),
        "error_count": len(error_payloads),
        "errors": error_payloads,
        "nodes": [node.as_dict() for node in nodes],
    }


def main() -> int:
    """CLI entrypoint. Returns non-zero when dependency trace validation fails."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_TRACE_INPUT_PATH)
    parser.add_argument("--json-report", type=Path, default=Path("generated/trace_matrix.json"))
    parser.add_argument("--markdown-report", type=Path, default=Path("generated/trace_matrix.md"))
    parser.add_argument("--csv-report", type=Path, default=Path("generated/trace_matrix.csv"))
    args = parser.parse_args()

    nodes = load_trace_nodes(args.input)
    report = validate_trace_nodes(nodes)
    generate_reports(report, args.json_report, args.markdown_report, args.csv_report)

    if report["status"] == "fail":
        print(f"Dependency trace validation failed with {report['error_count']} error(s).")
        for error in report["errors"]:
            print(f"- {error['code']}: {error['message']}")
        return 1

    print("Dependency trace validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
