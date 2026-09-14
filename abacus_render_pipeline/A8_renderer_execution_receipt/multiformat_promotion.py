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

from closed_loop import run as run_closed_loop
from semantic_delta_replay import run as run_replay
from multiformat_validation import load_and_validate_multiformat_receipt

EXECUTION_RECEIPT = HERE / "receipts" / "multiformat_execution_receipt.json"
PROMOTION_RECEIPT = HERE / "receipts" / "multiformat_promotion_receipt.json"


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def promote_multiformat(receipt_path: Path = EXECUTION_RECEIPT) -> dict[str, Any]:
    error: str | None = None
    execution: dict[str, Any] | None = None
    try:
        execution = load_and_validate_multiformat_receipt(receipt_path)
    except Exception as exc:
        error = str(exc)

    closed_loop = run_closed_loop()
    replay = run_replay()

    checks = {
        "execution_receipt_independently_revalidated": execution is not None,
        "required_formats_exact": bool(execution) and execution.get("required_formats") == ["pptx", "pdf"],
        "pptx_accepted": bool(execution) and execution["artifacts"]["pptx"]["decision"] == "accept",
        "pdf_accepted": bool(execution) and execution["artifacts"]["pdf"]["decision"] == "accept",
        "cross_format_parity": bool(execution) and bool(execution["cross_format_parity"]["pass"]),
        "receipt_replay_passed": bool(execution) and bool(execution["semantic_replay"]["pass"]),
        "closed_loop_passed": closed_loop.get("status") == "PASS",
        "semantic_delta_replay_passed": replay.get("status") == "PASS",
        "replay_ready": bool(closed_loop.get("runtime", {}).get("state", {}).get("replay_ready")),
        "traceable_tuple_count": closed_loop.get("completeness", {}).get("tuple_count", 0) >= 8,
    }
    allowed = all(checks.values())

    result: dict[str, Any] = {
        "promotion_receipt_version": "A8.2",
        "execution_receipt_sha256": sha256_path(receipt_path) if receipt_path.exists() else None,
        "source_commit": None if execution is None else execution.get("source_commit"),
        "publication_id": None if execution is None else execution.get("publication_id"),
        "required_formats": ["pptx", "pdf"],
        "artifact_sha256": None if execution is None else {
            "pptx": execution["artifacts"]["pptx"]["artifact_sha256"],
            "pdf": execution["artifacts"]["pdf"]["artifact_sha256"],
        },
        "ssot_sha256": None if execution is None else execution.get("ssot_sha256"),
        "tuple_ledger_sha256": None if execution is None else execution.get("tuple_ledger_sha256"),
        "checks": checks,
        "decision": "PROMOTE" if allowed else "REJECT",
        "validation_error": error,
        "authority_boundary": "GENERATED_OUTPUTS_REMAIN_NON_CANONICAL_DERIVATIVES",
    }

    PROMOTION_RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    PROMOTION_RECEIPT.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return result


if __name__ == "__main__":
    result = promote_multiformat()
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result["decision"] == "PROMOTE" else 1)
