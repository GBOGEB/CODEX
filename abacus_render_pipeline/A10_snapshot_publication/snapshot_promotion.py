from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
A9 = ROOT / "abacus_render_pipeline" / "A9_multiformat_publication"
A7 = ROOT / "abacus_render_pipeline" / "A7_executable_semantic_runtime"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(A7))

from closed_loop import run as run_closed_loop
from receipt_validation import load_and_validate
from semantic_delta_replay import run as run_replay

A9_RECEIPT = A9 / "receipts" / "multiformat_execution_receipt.json"
PROMOTION_RECEIPT = HERE / "receipts" / "snapshot_promotion_receipt.json"


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def evaluate() -> dict[str, Any]:
    snapshot = load_and_validate()
    a9 = json.loads(A9_RECEIPT.read_text(encoding="utf-8"))
    closed_loop = run_closed_loop()
    replay = run_replay()

    checks = {
        "a9_five_surface_receipt_accepted": a9.get("decision") == "accept" and len(a9.get("formats", {})) >= 5,
        "snapshot_execution_receipt_accepted": snapshot.get("decision") == "accept",
        "snapshot_content_address_revalidated": snapshot.get("snapshot_sha256") is not None,
        "source_commit_bound": snapshot.get("source_commit") == a9.get("source_commit"),
        "closed_loop_passed": closed_loop.get("status") == "PASS",
        "replay_passed": replay.get("status") == "PASS",
        "traceable_tuple_count": closed_loop.get("completeness", {}).get("tuple_count", 0) >= 13,
    }
    promote = all(checks.values())
    receipt = {
        "receipt_version": "A10.0",
        "publication_id": snapshot["publication_id"],
        "source_commit": snapshot["source_commit"],
        "surfaces": sorted(list(a9["formats"].keys()) + ["snapshot_png"]),
        "a9_receipt_sha256": sha256_path(A9_RECEIPT),
        "snapshot_receipt_sha256": sha256_path(HERE / "receipts" / "snapshot_execution_receipt.json"),
        "snapshot_sha256": snapshot["snapshot_sha256"],
        "checks": checks,
        "decision": "PROMOTE" if promote else "REJECT",
        "closed_loop_summary": closed_loop.get("completeness", {}),
        "replay_summary": replay.get("final_state", {}),
    }
    PROMOTION_RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    PROMOTION_RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return receipt


if __name__ == "__main__":
    result = evaluate()
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result["decision"] == "PROMOTE" else 1)
