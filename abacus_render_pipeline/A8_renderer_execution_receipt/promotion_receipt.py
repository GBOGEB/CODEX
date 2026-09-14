from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
A7 = ROOT / "abacus_render_pipeline" / "A7_executable_semantic_runtime"
sys.path.insert(0, str(A7))

from semantic_acceptance_gate import evaluate

EXECUTION_RECEIPT = HERE / "receipts" / "renderer_execution_receipt.json"
PROMOTION_RECEIPT = HERE / "receipts" / "promotion_receipt.json"


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def promote(receipt_path: Path = EXECUTION_RECEIPT) -> dict[str, Any]:
    acceptance = evaluate(receipt_path)
    execution = json.loads(receipt_path.read_text(encoding="utf-8"))
    decision = "PROMOTE" if acceptance["status"] == "PASS" else "REJECT"

    result = {
        "promotion_receipt_version": "A8.0",
        "execution_receipt_sha256": sha256_path(receipt_path),
        "artifact_sha256": execution["artifact_sha256"],
        "ssot_sha256": execution["ssot_sha256"],
        "tuple_ledger_sha256": execution["tuple_ledger_sha256"],
        "source_commit": execution.get("source_commit"),
        "semantic_acceptance_status": acceptance["status"],
        "semantic_promotions_allowed": acceptance["semantic_promotions_allowed"],
        "decision": decision,
        "checks": acceptance["checks"],
    }

    PROMOTION_RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    PROMOTION_RECEIPT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    result = promote()
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result["decision"] == "PROMOTE" else 1)
