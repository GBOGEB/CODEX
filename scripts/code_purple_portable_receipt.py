#!/usr/bin/env python3
"""Byte-bound advisory PAY_IT_FORWARD packet verifier, never a native approval.

Keeps CODEX code_purple_iteration.py as canonical method/admission projector.
This adapter checks actual supplied portable payload bytes against declared
producer/consumer receipts. Native source assertions remain untrusted.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
from pathlib import Path

PROJECTOR = Path(__file__).resolve().with_name("code_purple_iteration.py")
SPEC = importlib.util.spec_from_file_location("code_purple_iteration", PROJECTOR)
cp = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(cp)
REPO = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\Z")
ASSETS = {"schema", "test_fixture", "preflight", "repair_recipe", "dashboard"}


def canonical_bytes(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False).encode("utf-8")


def verify(record, source_payload, consumer_payload):
    if (not isinstance(record, dict) or not isinstance(source_payload, dict)
            or not isinstance(consumer_payload, dict)):
        raise ValueError("record and both payloads must be objects")
    projection = cp.project(record)  # Canonical CODEX owner, not a duplicate.
    reasons = []
    source_repo, target_repo = record.get("repo"), record.get("consumer_repo")
    if (not isinstance(source_repo, str) or not REPO.fullmatch(source_repo)
            or not isinstance(target_repo, str) or not REPO.fullmatch(target_repo)
            or source_repo == target_repo):
        reasons.append("ADJACENT_REPOSITORY_REQUIRED")
    if record.get("portable_asset_type") not in ASSETS:
        reasons.append("UNSUPPORTED_PORTABLE_ASSET")
    if record.get("sanitized") is not True:
        reasons.append("SANITIZATION_NOT_PROVEN")
    if projection["pay_it_forward"] != "CONSUMER_PROVEN_CANDIDATE":
        reasons.append("CODE_PURPLE_FORWARD_GATES_UNPROVEN")
    actual_source = hashlib.sha256(canonical_bytes(source_payload)).hexdigest()
    actual_consumer = hashlib.sha256(canonical_bytes(consumer_payload)).hexdigest()
    if actual_source != record.get("source_receipt_sha256"):
        reasons.append("SOURCE_RECEIPT_BYTES_MISMATCH")
    if actual_consumer != record.get("consumer_receipt_sha256"):
        reasons.append("CONSUMER_RECEIPT_BYTES_MISMATCH")
    if source_payload.get("source_sha") != record.get("observed_head_sha"):
        reasons.append("SOURCE_PAYLOAD_HEAD_MISMATCH")
    if consumer_payload.get("source_sha") != record.get("consumer_head_sha"):
        reasons.append("CONSUMER_PAYLOAD_HEAD_MISMATCH")
    if (source_payload.get("authority_transfer") is not False
            or consumer_payload.get("authority_transfer") is not False):
        reasons.append("PAYLOAD_AUTHORITY_TRANSFER_FORBIDDEN")
    if source_payload.get("asset_type") != record.get("portable_asset_type"):
        reasons.append("SOURCE_ASSET_TYPE_MISMATCH")
    if consumer_payload.get("source_receipt_sha256") != record.get("source_receipt_sha256"):
        reasons.append("CONSUMER_NOT_BOUND_TO_SOURCE_RECEIPT")
    if record.get("current_head_sha") != record.get("observed_head_sha"):
        reasons.append("STALE_SOURCE_HEAD")
    if (record.get("native_source_readback") is not True
            or record.get("native_consumer_readback") is not True):
        reasons.append("NATIVE_READBACK_UNVERIFIED")
    return {
        "schema": "code-purple.portable-receipt-projection.v1",
        "classification": "CANDIDATE_FOR_INDEPENDENT_ADMISSION" if not reasons else "HOLD",
        "reasons": sorted(set(reasons)), "source_repo": source_repo,
        "target_repo": target_repo,
        "byte_bound": (actual_source == record.get("source_receipt_sha256")
                       and actual_consumer == record.get("consumer_receipt_sha256")),
        "native_readback_claimed": (record.get("native_source_readback") is True
                                    and record.get("native_consumer_readback") is True),
        "independent_native_verification_performed": False,
        "merge_authorized": False, "dispatch_authorized": False,
        "authority_transfer": False, "formal_credit_delta": 0,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("observation", type=Path)
    parser.add_argument("producer_payload", type=Path)
    parser.add_argument("consumer_payload", type=Path)
    args = parser.parse_args(argv)
    output = verify(json.loads(args.observation.read_text(encoding="utf-8")),
                    json.loads(args.producer_payload.read_text(encoding="utf-8")),
                    json.loads(args.consumer_payload.read_text(encoding="utf-8")))
    print(json.dumps(output, sort_keys=True, indent=2))
    return 0 if output["classification"] == "CANDIDATE_FOR_INDEPENDENT_ADMISSION" else 2


if __name__ == "__main__":
    raise SystemExit(main())
