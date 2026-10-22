from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List

from closed_loop import DATA, load_json

LOCK_PATH = DATA / "lineage_lock.json"

# Fields that define what a tuple *is*. progress, todo and delta may evolve;
# changing an identity field rewrites history and is rejected.
IDENTITY_FIELDS = ("id", "parent", "branch", "theme", "intent")


def identity_sha256(item: Dict[str, Any]) -> str:
    identity = {field: item.get(field) for field in IDENTITY_FIELDS}
    payload = json.dumps(identity, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def lock_entries(tuples: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    return [{"id": item["id"], "identity_sha256": identity_sha256(item)} for item in tuples]


def check_append_only(tuples: List[Dict[str, Any]], locked: List[Dict[str, str]]) -> Dict[str, Any]:
    """Iterative pillar: new tuples extend prior state without deleting or rewriting lineage."""
    errors: List[str] = []
    current = lock_entries(tuples)
    for position, entry in enumerate(locked):
        if position >= len(current):
            errors.append(f"locked tuple {entry['id']} was deleted")
            continue
        observed = current[position]
        if observed["id"] != entry["id"]:
            errors.append(f"position {position + 1}: locked {entry['id']} replaced or reordered by {observed['id']}")
        elif observed["identity_sha256"] != entry["identity_sha256"]:
            errors.append(f"locked tuple {entry['id']} identity fields were rewritten")
    appended = [entry["id"] for entry in current[len(locked):]]
    return {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "locked_count": len(locked),
        "appended": appended,
    }


def extend_lock(tuples: List[Dict[str, Any]], locked: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Return the lock extended by appended tuples; refuse to rewrite locked history."""
    result = check_append_only(tuples, locked)
    if result["status"] != "PASS":
        raise ValueError("; ".join(result["errors"]))
    return locked + lock_entries(tuples)[len(locked):]


def load_lock(path: Path = LOCK_PATH) -> List[Dict[str, str]]:
    return load_json(path).get("locked", []) if path.exists() else []


def write_lock(entries: List[Dict[str, str]], path: Path = LOCK_PATH) -> None:
    doc = {"identity_fields": list(IDENTITY_FIELDS), "locked": entries}
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(doc, handle, indent=2)
        handle.write("\n")


def run() -> Dict[str, Any]:
    tuples = load_json(DATA / "semantic_tuple_ledger.json").get("tuples", [])
    result = check_append_only(tuples, load_lock())
    if not LOCK_PATH.exists():
        result["status"] = "FAIL"
        result["errors"].append(f"lineage lock missing: {LOCK_PATH.name}")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check or extend the append-only tuple lineage lock.")
    parser.add_argument("--extend", action="store_true", help="lock newly appended tuples")
    args = parser.parse_args()
    if args.extend:
        tuples = load_json(DATA / "semantic_tuple_ledger.json").get("tuples", [])
        write_lock(extend_lock(tuples, load_lock()))
    result = run()
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["status"] == "PASS" else 1)
