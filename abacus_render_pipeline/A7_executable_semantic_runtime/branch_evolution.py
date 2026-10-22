from __future__ import annotations

import json
from typing import Any, Dict, List, Set

from closed_loop import DATA, load_json, validate_records

REQUIRED_COMPETITION_FIELDS = {"id", "fork", "alternatives", "status", "winner", "evidence"}
COMPETITION_STATUSES = {"open", "converged"}


def children_by_parent(tuples: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    children: Dict[str, List[str]] = {}
    for item in tuples:
        parent = item.get("parent")
        if parent is not None:
            children.setdefault(parent, []).append(item["id"])
    return children


def fork_points(tuples: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    """Tuples with two or more children, in ledger order."""
    return {parent: kids for parent, kids in children_by_parent(tuples).items() if len(kids) > 1}


def frontier(tuples: List[Dict[str, Any]]) -> List[str]:
    """Leaf tuples: the current growing tips of every branch."""
    parents = set(children_by_parent(tuples))
    return [item["id"] for item in tuples if item["id"] not in parents]


def descendants(tuples: List[Dict[str, Any]], root: str) -> Set[str]:
    children = children_by_parent(tuples)
    found: Set[str] = set()
    pending = list(children.get(root, []))
    while pending:
        node = pending.pop()
        if node not in found:
            found.add(node)
            pending.extend(children.get(node, []))
    return found


def validate_competitions(tuples: List[Dict[str, Any]], competitions: List[Dict[str, Any]]) -> List[str]:
    """Enforce INV-005: competing branches stay explicit until cited evidence supports convergence."""
    errors = validate_records(competitions, REQUIRED_COMPETITION_FIELDS, "competition")
    if errors:
        return errors

    by_id = {item["id"]: item for item in tuples}
    for competition in competitions:
        cid = competition["id"]
        fork = competition["fork"]
        alternatives = competition["alternatives"]
        status = competition["status"]
        winner = competition["winner"]
        evidence = competition["evidence"]

        if fork not in by_id:
            errors.append(f"{cid} fork {fork} is not in the tuple ledger")
            continue
        if not isinstance(alternatives, list) or len(alternatives) < 2:
            errors.append(f"{cid} must name at least two alternatives")
            continue
        if len(set(alternatives)) != len(alternatives):
            errors.append(f"{cid} lists duplicate alternatives")
        for alternative in alternatives:
            if alternative not in by_id:
                # A converged loser must stay in the ledger: lineage is never deleted.
                errors.append(f"{cid} alternative {alternative} is not in the tuple ledger")
            elif by_id[alternative].get("parent") != fork:
                errors.append(f"{cid} alternative {alternative} does not branch from fork {fork}")

        if status not in COMPETITION_STATUSES:
            errors.append(f"{cid} has unknown status {status}")
        elif status == "open":
            if winner is not None:
                errors.append(f"{cid} is open but names winner {winner}")
        else:
            if winner not in alternatives:
                errors.append(f"{cid} converged winner {winner} is not one of its alternatives")
            if not isinstance(evidence, list) or not evidence:
                errors.append(f"{cid} converged without evidence")
            else:
                after_fork = descendants(tuples, fork)
                for ref in evidence:
                    if ref not in after_fork:
                        errors.append(f"{cid} evidence {ref} is not a tuple descending from fork {fork}")
    return errors


def evaluate(tuples: List[Dict[str, Any]], competitions: List[Dict[str, Any]]) -> Dict[str, Any]:
    errors = validate_competitions(tuples, competitions)
    by_id = {item["id"]: item for item in tuples}
    open_items = [c for c in competitions if c.get("status") == "open"]
    competing_branches = sorted(
        {by_id[alt]["branch"] for c in open_items for alt in c.get("alternatives", []) if alt in by_id}
    )
    return {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "fork_points": fork_points(tuples),
        "frontier": frontier(tuples),
        "open_competitions": [c["id"] for c in open_items],
        "converged_competitions": [c["id"] for c in competitions if c.get("status") == "converged"],
        "competing_branches": competing_branches,
    }


def run() -> Dict[str, Any]:
    tuple_doc = load_json(DATA / "semantic_tuple_ledger.json")
    governance = load_json(DATA / "governance_ledger.json")
    return evaluate(tuple_doc.get("tuples", []), governance.get("branch_competition", []))


if __name__ == "__main__":
    result = run()
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["status"] == "PASS" else 1)
