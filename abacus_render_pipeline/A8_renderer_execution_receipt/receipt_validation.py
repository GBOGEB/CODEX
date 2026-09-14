from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SCHEMA = HERE / "receipt_schema.json"
ARTIFACT = HERE / "outputs" / "reference_render.html"
SSOT = HERE / "ssot" / "reference_publication.yaml"
TUPLE_LEDGER = ROOT / "abacus_render_pipeline" / "A7_executable_semantic_runtime" / "data" / "semantic_tuple_ledger.json"


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_and_validate_receipt(receipt_path: Path) -> dict[str, Any]:
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    errors = sorted(Draft202012Validator(schema).iter_errors(receipt), key=lambda e: list(e.path))
    if errors:
        raise ValueError("receipt schema validation failed: " + "; ".join(error.message for error in errors))

    expected_hashes = {
        "artifact_sha256": sha256_path(ARTIFACT),
        "ssot_sha256": sha256_path(SSOT),
        "tuple_ledger_sha256": sha256_path(TUPLE_LEDGER),
    }
    mismatches = [
        f"{field}: receipt={receipt.get(field)} actual={actual}"
        for field, actual in expected_hashes.items()
        if receipt.get(field) != actual
    ]
    if mismatches:
        raise ValueError("receipt content-address validation failed: " + "; ".join(mismatches))

    check_passes = [bool(value.get("pass")) for value in receipt["checks"].values()]
    expected_decision = "accept" if all(check_passes) else "reject"
    if receipt["decision"] != expected_decision:
        raise ValueError(
            f"receipt decision inconsistent with checks: receipt={receipt['decision']} expected={expected_decision}"
        )

    return receipt


if __name__ == "__main__":
    path = HERE / "receipts" / "renderer_execution_receipt.json"
    validated = load_and_validate_receipt(path)
    print(json.dumps({"status": "PASS", "decision": validated["decision"]}, indent=2))
