from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from closed_loop import DATA, load_json, validate_parentage, validate_records, REQUIRED_TUPLE_FIELDS


def replay(tuples: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Replay the governed tuple ledger in source order and emit cumulative state."""
    schema_errors = validate_records(tuples, REQUIRED_TUPLE_FIELDS, "tuple")
    parent_errors = validate_parentage(tuples)
    if schema_errors or parent_errors:
        return {
            "status": "FAIL",
            "errors": schema_errors + parent_errors,
            "steps": [],
        }

    visited = set()
    branches = set()
    completed = set()
    active = set()
    steps = []

    for position, item in enumerate(tuples, start=1):
        parent = item.get("parent")
        if parent is not None and parent not in visited:
            return {
                "status": "FAIL",
                "errors": [f"replay order invalid at {item['id']}: parent {parent} has not been replayed"],
                "steps": steps,
            }

        visited.add(item["id"])
        branches.add(item["branch"])
        progress = str(item.get("progress", "")).lower()
        if progress.startswith("complete"):
            completed.add(item["id"])
            active.discard(item["id"])
        else:
            active.add(item["id"])

        steps.append(
            {
                "position": position,
                "tuple_id": item["id"],
                "parent": parent,
                "branch": item["branch"],
                "intent": item["intent"],
                "progress": item["progress"],
                "todo": item["todo"],
                "state_after": {
                    "visited_count": len(visited),
                    "branch_count": len(branches),
                    "completed_count": len(completed),
                    "active_count": len(active),
                },
            }
        )

    expected_ids = [f"TUP-{index:04d}" for index in range(1, 9)]
    actual_ids = [item["id"] for item in tuples]
    exact_expected_sequence = actual_ids[:8] == expected_ids

    return {
        "status": "PASS" if exact_expected_sequence else "FAIL",
        "errors": [] if exact_expected_sequence else [
            f"expected first eight tuple IDs {expected_ids}, observed {actual_ids[:8]}"
        ],
        "mode": "semantic_delta_replay",
        "steps": steps,
        "final_state": {
            "last_tuple": actual_ids[-1] if actual_ids else None,
            "visited_count": len(visited),
            "branch_count": len(branches),
            "completed_count": len(completed),
            "active_count": len(active),
            "exact_TUP_0001_to_TUP_0008": exact_expected_sequence,
        },
    }


def run() -> Dict[str, Any]:
    tuple_doc = load_json(DATA / "semantic_tuple_ledger.json")
    return replay(tuple_doc.get("tuples", []))


if __name__ == "__main__":
    result = run()
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["status"] == "PASS" else 1)
