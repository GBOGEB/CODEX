from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict

from closed_loop import run as run_closed_loop
from semantic_delta_replay import run as run_replay

ROOT = Path(__file__).resolve().parents[2]
A8 = ROOT / "abacus_render_pipeline" / "A8_renderer_execution_receipt"
sys.path.insert(0, str(A8))

from receipt_validation import load_and_validate_receipt

DEFAULT_RECEIPT = A8 / "receipts" / "renderer_execution_receipt.json"


def evaluate(receipt_path: Path | None = None) -> Dict[str, Any]:
    receipt_path = receipt_path or DEFAULT_RECEIPT
    closed_loop = run_closed_loop()
    replay = run_replay()

    receipt_error = None
    receipt: Dict[str, Any] | None = None
    try:
        receipt = load_and_validate_receipt(receipt_path)
    except Exception as exc:  # gate must turn malformed evidence into rejection, not crash promotion logic
        receipt_error = str(exc)

    receipt_checks_pass = bool(receipt) and all(
        bool(value.get("pass")) for value in receipt.get("checks", {}).values()
    )
    receipt_replay_pass = bool(receipt) and bool(
        receipt.get("checks", {}).get("semantic_replay", {}).get("pass")
    )

    checks = {
        "renderer_execution_receipt_valid": receipt is not None,
        "renderer_execution_accepted": bool(receipt) and receipt.get("decision") == "accept",
        "renderer_checks_passed": receipt_checks_pass,
        "schema_parentage_reconstruction_dag_completeness_passed": closed_loop["status"] == "PASS",
        "semantic_delta_replay_passed": replay["status"] == "PASS",
        "receipt_semantic_replay_passed": receipt_replay_pass,
        "replay_ready": bool(closed_loop["runtime"]["state"]["replay_ready"]),
        "traceable_tuple_count": closed_loop["completeness"]["tuple_count"] >= 8,
    }

    promotions_allowed = all(checks.values())
    return {
        "status": "PASS" if promotions_allowed else "FAIL",
        "semantic_promotions_allowed": promotions_allowed,
        "checks": checks,
        "receipt_error": receipt_error,
        "receipt_summary": None if receipt is None else {
            "artifact_sha256": receipt["artifact_sha256"],
            "ssot_sha256": receipt["ssot_sha256"],
            "tuple_ledger_sha256": receipt["tuple_ledger_sha256"],
            "renderer_version": receipt["renderer_version"],
            "theme": receipt["theme"],
            "render_mode": receipt["render_mode"],
            "decision": receipt["decision"],
        },
        "closed_loop_summary": {
            "tuple_count": closed_loop["completeness"]["tuple_count"],
            "invariant_count": closed_loop["completeness"]["invariant_count"],
            "debt_count": closed_loop["completeness"]["debt_count"],
            "completeness_score": closed_loop["completeness"]["score"],
        },
        "replay_summary": replay.get("final_state", {}),
    }


if __name__ == "__main__":
    result = evaluate()
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["status"] == "PASS" else 1)
