from __future__ import annotations

import json
from typing import Any, Dict, List, Tuple

from closed_loop import (
    DATA,
    REQUIRED_DEBT_FIELDS,
    REQUIRED_INVARIANT_FIELDS,
    REQUIRED_TUPLE_FIELDS,
    completeness,
    derive_branch_dag,
    load_json,
    validate_parentage,
    validate_records,
)
from runtime import reconstruct, validate
from semantic_acceptance_gate import evaluate
from semantic_delta_replay import replay


def run_first_red() -> Dict[str, Any]:
    tuple_doc = load_json(DATA / "semantic_tuple_ledger.json")
    governance = load_json(DATA / "governance_ledger.json")
    tuples = tuple_doc.get("tuples", [])
    invariants = governance.get("invariants", [])
    debt = governance.get("semantic_debt", [])

    stages: List[Tuple[str, bool, Any]] = []

    schema_errors = []
    schema_errors += validate_records(tuples, REQUIRED_TUPLE_FIELDS, "tuple")
    schema_errors += validate_records(invariants, REQUIRED_INVARIANT_FIELDS, "invariant")
    schema_errors += validate_records(debt, REQUIRED_DEBT_FIELDS, "debt")
    stages.append(("schema", not schema_errors, schema_errors))

    parent_errors = validate_parentage(tuples)
    stages.append(("parentage", not parent_errors, parent_errors))

    runtime_result = validate(reconstruct(tuples, invariants, debt))
    stages.append(("reconstruction", runtime_result["status"] == "PASS", runtime_result))

    dag = derive_branch_dag(tuples)
    expected_edges = max(len(tuples) - 1, 0)
    dag_ok = len(dag["nodes"]) == len(tuples) and len(dag["edges"]) == expected_edges
    stages.append(("DAG", dag_ok, {"nodes": len(dag["nodes"]), "edges": len(dag["edges"]), "expected_edges": expected_edges}))

    completeness_result = completeness(tuples, invariants, debt)
    completeness_ok = completeness_result["score"] == 1.0
    stages.append(("completeness", completeness_ok, completeness_result))

    replay_result = replay(tuples)
    stages.append(("semantic_delta_replay", replay_result["status"] == "PASS", replay_result.get("final_state", replay_result)))

    acceptance = evaluate()
    stages.append(("renderer_execution_receipt_acceptance", acceptance["status"] == "PASS", acceptance))

    stage_results = []
    first_red = None
    for name, passed, detail in stages:
        stage_results.append({"stage": name, "status": "PASS" if passed else "FAIL", "detail": detail})
        if not passed and first_red is None:
            first_red = name

    return {
        "status": "PASS" if first_red is None else "FAIL",
        "first_red": first_red,
        "stages": stage_results,
    }


if __name__ == "__main__":
    result = run_first_red()
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["status"] == "PASS" else 1)
