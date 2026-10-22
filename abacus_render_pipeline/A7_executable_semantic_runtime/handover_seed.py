from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from branch_evolution import evaluate as evaluate_branch_evolution
from closed_loop import DATA, load_json
from runtime import reconstruct, validate

SEED_PATH = DATA / "handover_seed.json"
SEED_VERSION = "A7.4"
CLOSED_DEBT = {"closed", "resolved", "done"}


def canonical_sha256(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def ledger_sha256(tuple_doc: Dict[str, Any], governance: Dict[str, Any]) -> str:
    """Digest of the parsed ledgers, so checkout line endings cannot change it."""
    return canonical_sha256({"tuple_ledger": tuple_doc, "governance_ledger": governance})


def build_seed(
    tuple_doc: Dict[str, Any],
    governance: Dict[str, Any],
    parent_seed_sha256: Optional[str] = None,
) -> Dict[str, Any]:
    """Recursive pillar: the reconstructed state, packaged to start the next handover."""
    tuples = tuple_doc.get("tuples", [])
    invariants = governance.get("invariants", [])
    debt = governance.get("semantic_debt", [])
    by_id = {item["id"]: item for item in tuples}

    state = validate(reconstruct(tuples, invariants, debt))["state"]
    evolution = evaluate_branch_evolution(tuples, governance.get("branch_competition", []))

    body = {
        "seed_version": SEED_VERSION,
        "ledger_sha256": ledger_sha256(tuple_doc, governance),
        "parent_seed_sha256": parent_seed_sha256,
        "state": state,
        "resume_from": [
            {"id": tid, "branch": by_id[tid]["branch"], "todo": by_id[tid].get("todo")}
            for tid in evolution["frontier"]
        ],
        "open_competitions": evolution["open_competitions"],
        "competing_branches": evolution["competing_branches"],
        "open_debt": [
            {"id": item["id"], "topic": item.get("topic"), "next_action": item.get("next_action")}
            for item in debt
            if str(item.get("status", "open")).lower() not in CLOSED_DEBT
        ],
        "invariant_ids": [item["id"] for item in invariants],
    }
    return {**body, "seed_sha256": canonical_sha256(body)}


def next_seed(
    tuple_doc: Dict[str, Any],
    governance: Dict[str, Any],
    previous: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Unchanged ledgers keep the previous seed; changed ledgers chain a new seed onto it."""
    if previous and previous.get("ledger_sha256") == ledger_sha256(tuple_doc, governance):
        return previous
    return build_seed(tuple_doc, governance, previous["seed_sha256"] if previous else None)


def verify_seed(seed: Dict[str, Any], tuple_doc: Dict[str, Any], governance: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    body = {key: value for key, value in seed.items() if key != "seed_sha256"}
    if canonical_sha256(body) != seed.get("seed_sha256"):
        errors.append("seed_sha256 does not match seed content")
    if seed.get("ledger_sha256") != ledger_sha256(tuple_doc, governance):
        errors.append("seed is stale: ledgers changed since it was written; run python handover_seed.py --write")
    elif build_seed(tuple_doc, governance, seed.get("parent_seed_sha256")) != seed:
        errors.append("seed content does not match the state reconstructed from the ledgers")
    return errors


def load_ledgers() -> tuple[Dict[str, Any], Dict[str, Any]]:
    return load_json(DATA / "semantic_tuple_ledger.json"), load_json(DATA / "governance_ledger.json")


def write_seed(seed: Dict[str, Any], path: Path = SEED_PATH) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(seed, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def run() -> Dict[str, Any]:
    if not SEED_PATH.exists():
        return {"status": "FAIL", "errors": [f"handover seed missing: {SEED_PATH.name}"]}
    seed = load_json(SEED_PATH)
    errors = verify_seed(seed, *load_ledgers())
    return {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "seed_sha256": seed.get("seed_sha256"),
        "parent_seed_sha256": seed.get("parent_seed_sha256"),
        "resume_from": [item["id"] for item in seed.get("resume_from", [])],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check or write the recursive handover seed.")
    parser.add_argument("--write", action="store_true", help="chain a new seed when the ledgers changed")
    args = parser.parse_args()
    if args.write:
        previous = load_json(SEED_PATH) if SEED_PATH.exists() else None
        write_seed(next_seed(*load_ledgers(), previous))
    result = run()
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["status"] == "PASS" else 1)
