#!/usr/bin/env python3
"""Read-only Code Purple iteration projector.

Derives the smallest method path and first material failure from a bounded JSON
observation. This is not a merge gate, self-modifying agent or domain authority.
GitHub remains the native admission source of truth.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

FULL_SHA = re.compile(r"[0-9a-f]{40}\Z")
FULL_DIGEST = re.compile(r"[0-9a-f]{64}\Z")
RED_CONCLUSIONS = {"failure", "timed_out", "cancelled", "action_required"}
ALLOWED_CONCLUSIONS = RED_CONCLUSIONS | {"success", "neutral", "skipped"}


def method_path(record: dict[str, Any]) -> list[str]:
    """Select only methods backed by a real predicate, never ceremonial loops."""
    sequence = ["3PR"]
    if record.get("structural_gap_observed") or record.get("recurrence_gap_observed"):
        sequence.append("MIP")
    if record.get("transaction_required"):
        sequence.append("3PC")
    if record.get("local_dov_proven") and record.get("generalisation_gap_observed"):
        sequence.append("3P3")
    return sequence


def first_material_red(checks: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Return earliest completed material failing check, not first screenshot red."""
    completed = [
        c for c in checks
        if c.get("status") == "completed"
        and c.get("conclusion") in RED_CONCLUSIONS
        and c.get("material", True)
    ]
    if not completed:
        return None
    return min(completed, key=lambda c: (int(c.get("completed_order", 10**9)), str(c.get("name", ""))))


def project(record: dict[str, Any]) -> dict[str, Any]:
    repo = record.get("repo")
    head = record.get("observed_head_sha")
    checks = record.get("checks", [])
    if not isinstance(repo, str) or not repo:
        raise ValueError("repo is required")
    if not isinstance(head, str) or FULL_SHA.fullmatch(head) is None:
        raise ValueError("observed_head_sha must be a full lowercase 40-char SHA")
    if not isinstance(checks, list):
        raise ValueError("checks must be a list")
    for c in checks:
        if not isinstance(c, dict) or not isinstance(c.get("name"), str):
            raise ValueError("every check requires a name")
        if c.get("conclusion") not in ALLOWED_CONCLUSIONS | {None}:
            raise ValueError("unrecognized check conclusion")
        if c.get("status") not in {"queued", "in_progress", "completed", "pending"}:
            raise ValueError("unrecognized check status")
    names = [c["name"] for c in checks]
    if len(names) != len(set(names)):
        raise ValueError("duplicate check names require disambiguated check identifiers")

    required = record.get("required_checks", [])
    if not isinstance(required, list):
        raise ValueError("required_checks must be a list")
    by_name = {c["name"]: c for c in checks}
    missing_required = [
        n for n in required
        if n not in by_name or by_name[n].get("status") != "completed"
        or by_name[n].get("conclusion") != "success"
    ]
    red = first_material_red(checks)
    same_head = record.get("current_head_sha") == head
    reviews_ok = record.get("code_review_complete") is True
    security_ok = record.get("security_review_complete") is True
    unresolved = record.get("unresolved_threads", None)
    threads_ok = type(unresolved) is int and unresolved == 0
    executed = record.get("executed_steps", 0)
    execution_ok = type(executed) is int and executed > 0
    proofs_ok = bool(required) and not missing_required and reviews_ok and security_ok and threads_ok and execution_ok

    if not same_head:
        state, action = "HOLD", "REFRESH_EXACT_HEAD"
    elif red:
        state, action = "REPAIR_REENTRY", "REPAIR_FIRST_COMPLETED_MATERIAL_RED"
    elif not proofs_ok:
        state, action = "HOLD", "WAIT_OR_REPAIR_ADMISSION_EVIDENCE"
    else:
        state, action = "ADMISSION_CANDIDATE", "VERIFY_REPOSITORY_NATIVE_GATE"
    # 'ADMISSION_CANDIDATE' deliberately never equals an authoritative PASS/merge.
    forward_requested = record.get("pay_it_forward_requested") is True
    source_receipt = record.get("source_receipt_sha256")
    consumer_receipt = record.get("consumer_receipt_sha256")
    consumer_sha = record.get("consumer_head_sha")
    consumer_proof = (
        forward_requested
        and same_head
        and proofs_ok
        and isinstance(source_receipt, str) and bool(FULL_DIGEST.fullmatch(source_receipt))
        and isinstance(consumer_receipt, str) and bool(FULL_DIGEST.fullmatch(consumer_receipt))
        and isinstance(consumer_sha, str) and bool(FULL_SHA.fullmatch(consumer_sha))
        and record.get("local_dov_proven") is True
        and record.get("generalisation_gap_observed") is True
        and record.get("sanitized") is True
        and record.get("consumer_independent_proof") is True
        and record.get("consumer_accepted") is True
    )
    forward = ("CONSUMER_PROVEN_CANDIDATE" if consumer_proof
               else "CONSUMER_PENDING" if forward_requested else "NOT_REQUESTED")
    return {
        "schema": "code-purple.iteration-projection/0.1",
        "repo": repo,
        "observed_head_sha": head,
        "classification": state,
        "next_action": action,
        "method_path": method_path(record),
        "first_material_red": None if red is None else red["name"],
        "required_checks_unproven": missing_required,
        "review_evidence_complete": reviews_ok and security_ok and threads_ok,
        "execution_evidence": "EXECUTED_GT_ZERO" if execution_ok else "WITHHELD",
        "pay_it_forward": forward,
        "receipt_kind": "ADVISORY_READ_ONLY",
        "repository_native_admission": "NOT_GRANTED",
        "authority_transfer": False,
        "formal_credit_delta": 0,
        "engineering_credit_delta": 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("observation", type=Path, help="JSON snapshot with exact observed SHA")
    args = parser.parse_args()
    record = json.loads(args.observation.read_text(encoding="utf-8"))
    print(json.dumps(project(record), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
