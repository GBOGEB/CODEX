from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from runtime import reconstruct, validate

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"

REQUIRED_TUPLE_FIELDS = {"id", "parent", "branch", "theme", "intent", "progress", "todo"}
REQUIRED_INVARIANT_FIELDS = {"id", "statement"}
REQUIRED_DEBT_FIELDS = {"id", "status", "topic", "next_action"}


def load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def validate_records(records: List[Dict[str, Any]], required: set[str], label: str) -> List[str]:
    errors: List[str] = []
    ids = set()
    for index, record in enumerate(records):
        missing = sorted(required - set(record))
        if missing:
            errors.append(f"{label}[{index}] missing fields: {', '.join(missing)}")
        record_id = record.get("id")
        if record_id in ids:
            errors.append(f"duplicate {label} id: {record_id}")
        ids.add(record_id)
    return errors


def validate_parentage(tuples: List[Dict[str, Any]]) -> List[str]:
    ids = {item["id"] for item in tuples if item.get("id")}
    errors = []
    for item in tuples:
        parent = item.get("parent")
        if parent is not None and parent not in ids:
            errors.append(f"{item.get('id')} references missing parent {parent}")
    return errors


def derive_branch_dag(tuples: List[Dict[str, Any]]) -> Dict[str, Any]:
    nodes = [
        {
            "id": item["id"],
            "branch": item["branch"],
            "theme": item["theme"],
            "progress": item["progress"],
        }
        for item in tuples
    ]
    edges = [
        {"from": item["parent"], "to": item["id"]}
        for item in tuples
        if item.get("parent")
    ]
    return {"nodes": nodes, "edges": edges}


def completeness(tuples, invariants, debt) -> Dict[str, Any]:
    tuple_required = len(tuples) > 0
    invariant_required = len(invariants) > 0
    parentage_ok = not validate_parentage(tuples)
    score = sum([tuple_required, invariant_required, parentage_ok]) / 3.0
    return {
        "score": round(score, 3),
        "tuple_count": len(tuples),
        "invariant_count": len(invariants),
        "debt_count": len(debt),
        "parentage_valid": parentage_ok,
    }


def run() -> Dict[str, Any]:
    tuple_doc = load_json(DATA / "semantic_tuple_ledger.json")
    governance = load_json(DATA / "governance_ledger.json")

    tuples = tuple_doc.get("tuples", [])
    invariants = governance.get("invariants", [])
    debt = governance.get("semantic_debt", [])

    schema_errors = []
    schema_errors += validate_records(tuples, REQUIRED_TUPLE_FIELDS, "tuple")
    schema_errors += validate_records(invariants, REQUIRED_INVARIANT_FIELDS, "invariant")
    schema_errors += validate_records(debt, REQUIRED_DEBT_FIELDS, "debt")
    schema_errors += validate_parentage(tuples)

    state = reconstruct(tuples, invariants, debt)
    runtime_validation = validate(state)
    dag = derive_branch_dag(tuples)

    status = "PASS" if not schema_errors and runtime_validation["status"] == "PASS" else "FAIL"
    return {
        "status": status,
        "schema_errors": schema_errors,
        "runtime": runtime_validation,
        "completeness": completeness(tuples, invariants, debt),
        "branch_dag": dag,
        "next_actions": [item["next_action"] for item in debt if item.get("status") == "open"],
    }


if __name__ == "__main__":
    result = run()
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["status"] == "PASS" else 1)
