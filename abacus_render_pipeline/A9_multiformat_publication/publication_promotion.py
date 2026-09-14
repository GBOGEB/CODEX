from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
A7 = ROOT / "abacus_render_pipeline" / "A7_executable_semantic_runtime"
sys.path.insert(0, str(A7))
sys.path.insert(0, str(HERE))

from closed_loop import run as run_closed_loop
from receipt_validation import load_and_validate_receipt
from semantic_delta_replay import run as run_replay

EXECUTION_RECEIPT = HERE / "receipts" / "multiformat_execution_receipt.json"
PROMOTION_RECEIPT = HERE / "receipts" / "publication_promotion_receipt.json"


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def evaluate(execution_receipt: Path = EXECUTION_RECEIPT) -> dict[str, Any]:
    receipt_error: str | None = None
    receipt: dict[str, Any] | None = None
    try:
        receipt = load_and_validate_receipt(execution_receipt)
    except Exception as exc:
        receipt_error = str(exc)

    closed_loop = run_closed_loop()
    replay = run_replay()
    format_acceptance = bool(receipt) and all(
        item.get("decision") == "accept" for item in receipt.get("formats", {}).values()
    )
    checks = {
        "multiformat_execution_receipt_valid": receipt is not None,
        "multiformat_execution_accepted": bool(receipt) and receipt.get("decision") == "accept",
        "all_format_receipts_accepted": format_acceptance,
        "cross_format_parity_passed": bool(receipt)
        and bool(receipt.get("cross_format_parity", {}).get("pass")),
        "schema_parentage_reconstruction_dag_completeness_passed": closed_loop["status"]
        == "PASS",
        "semantic_delta_replay_passed": replay["status"] == "PASS",
        "replay_ready": bool(closed_loop["runtime"]["state"]["replay_ready"]),
    }
    promote = all(checks.values())
    promotion = {
        "promotion_receipt_version": "A9.0",
        "decision": "PROMOTE" if promote else "REJECT",
        "checks": checks,
        "receipt_error": receipt_error,
        "execution_receipt_sha256": sha256_path(execution_receipt)
        if execution_receipt.exists()
        else None,
        "source_commit": None if receipt is None else receipt["source_commit"],
        "publication_id": None if receipt is None else receipt["publication_id"],
        "ssot_sha256": None if receipt is None else receipt["ssot_sha256"],
        "canonical_content_sha256": None
        if receipt is None
        else receipt["canonical_content_sha256"],
        "tuple_ledger_sha256": None if receipt is None else receipt["tuple_ledger_sha256"],
        "artifact_sha256": {}
        if receipt is None
        else {
            name: item["artifact_sha256"]
            for name, item in receipt["formats"].items()
        },
        "closed_loop_summary": {
            "tuple_count": closed_loop["completeness"]["tuple_count"],
            "invariant_count": closed_loop["completeness"]["invariant_count"],
            "debt_count": closed_loop["completeness"]["debt_count"],
            "completeness_score": closed_loop["completeness"]["score"],
        },
        "semantic_replay_summary": replay.get("final_state", {}),
    }
    PROMOTION_RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    PROMOTION_RECEIPT.write_text(
        json.dumps(promotion, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return promotion


if __name__ == "__main__":
    result = evaluate()
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result["decision"] == "PROMOTE" else 1)
