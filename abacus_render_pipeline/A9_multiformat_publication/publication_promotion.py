from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
A7 = ROOT / "abacus_render_pipeline" / "A7_executable_semantic_runtime"
sys.path.insert(0, str(A7))
sys.path.insert(0, str(HERE))

from closed_loop import run as run_closed_loop
from receipt_validation import (
    load_and_validate_hosted_pages_receipt,
    load_and_validate_receipt,
)
from semantic_delta_replay import run as run_replay

EXECUTION_RECEIPT = HERE / "receipts" / "multiformat_execution_receipt.json"
HOSTED_PAGES_RECEIPT = HERE / "receipts" / "github_pages_hosted_receipt.json"
PROMOTION_RECEIPT = HERE / "receipts" / "publication_promotion_receipt.json"


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def evaluate(
    execution_receipt: Path = EXECUTION_RECEIPT,
    hosted_pages_receipt: Path = HOSTED_PAGES_RECEIPT,
    *,
    refetch_hosted: bool | None = None,
) -> dict[str, Any]:
    receipt_error: str | None = None
    receipt: dict[str, Any] | None = None
    try:
        receipt = load_and_validate_receipt(execution_receipt)
    except Exception as exc:
        receipt_error = str(exc)

    verify_network = (
        os.environ.get("ABACUS_VERIFY_HOSTED_PAGES") == "1"
        if refetch_hosted is None
        else refetch_hosted
    )
    hosted_missing = not hosted_pages_receipt.exists()
    hosted_error: str | None = None
    hosted: dict[str, Any] | None = None
    if not hosted_missing and receipt is not None:
        try:
            hosted = load_and_validate_hosted_pages_receipt(
                hosted_pages_receipt,
                execution_receipt,
                refetch=verify_network,
            )
        except Exception as exc:
            hosted_error = str(exc)

    closed_loop = run_closed_loop()
    replay = run_replay()
    format_acceptance = bool(receipt) and all(
        item.get("decision") == "accept" for item in receipt.get("formats", {}).values()
    )
    base_checks = {
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
    hosted_checks = {
        "github_pages_hosted_receipt_present": not hosted_missing,
        "github_pages_hosted_receipt_valid": hosted is not None,
        "github_pages_hosted_hash_and_semantic_parity_revalidated": hosted is not None,
    }
    checks = {**base_checks, **hosted_checks}

    base_ok = all(base_checks.values())
    hosted_ok = all(hosted_checks.values())
    if base_ok and hosted_ok:
        decision = "PROMOTE"
    elif base_ok and hosted_missing:
        decision = "WITHHOLD"
    else:
        decision = "REJECT"

    promotion = {
        "promotion_receipt_version": "A9.1",
        "decision": decision,
        "checks": checks,
        "receipt_error": receipt_error,
        "hosted_pages_receipt_error": hosted_error,
        "hosted_pages_network_refetch_required": verify_network,
        "execution_receipt_sha256": sha256_path(execution_receipt)
        if execution_receipt.exists()
        else None,
        "hosted_pages_receipt_sha256": sha256_path(hosted_pages_receipt)
        if hosted_pages_receipt.exists()
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
        "hosted_pages": None
        if hosted is None
        else {
            "page_url": hosted["page_url"],
            "fetched_url": hosted.get("fetched_url"),
            "hosted_sha256": hosted["hosted_sha256"],
            "hosted_bytes": hosted["hosted_bytes"],
            "semantic_parity": hosted["semantic_parity"],
            "deployment_run_id": hosted.get("deployment_run_id"),
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


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--allow-withhold",
        action="store_true",
        help="Return success when all pre-deployment checks pass and hosted Pages evidence is deliberately absent.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    result = evaluate()
    print(json.dumps(result, indent=2, sort_keys=True))
    success = result["decision"] == "PROMOTE" or (
        args.allow_withhold and result["decision"] == "WITHHOLD"
    )
    raise SystemExit(0 if success else 1)
