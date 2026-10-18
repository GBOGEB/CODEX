#!/usr/bin/env python3
"""W2 read-only CODEX Swift roof P3: native pulse metrics and KEB->DOW->QPS join.

Source-bound, non-authoritative and deliberately incapable of accepting QPS,
merging code or promoting historical receipt parity into current-head proof.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import UTC, datetime
from pathlib import Path

from swift_roof_mip import CODEX, QPS, SHA, checked_head, verify_native, demand

ABACUS = "GBOGEB/ABACUS"
SCHEMA = "codepurple.swift.roof.p3.observation.v1"
TERMINAL = frozenset({"success", "failure", "cancelled", "skipped"})


def owner_history(history: dict) -> dict:
    demand(history.get("schema") == "codepurple.swift.owner_history.v1", "history schema")
    producer, consumer, child = (history.get(k) for k in ("producer", "abacus", "qps"))
    demand(all(isinstance(v, dict) for v in (producer, consumer, child)), "history participants missing")
    sha = producer.get("source_sha")
    digest = producer.get("receipt_sha256")
    demand(isinstance(sha, str) and SHA.fullmatch(sha) is not None, "historical source SHA")
    demand(type(digest) is str and len(digest) == 64 and
           all(c in "0123456789abcdef" for c in digest), "historical digest")
    demand(producer.get("repo") == CODEX and type(producer.get("run_id")) is int and
           producer["run_id"] > 0 and producer.get("workflow_jobs_success") == 2,
           "historical producer run")
    demand(consumer.get("repo") == ABACUS and child.get("repo") == QPS,
           "historical owner roles")
    for owner in (consumer, child):
        demand(owner.get("source_sha") == sha and owner.get("receipt_sha256") == digest,
               "historical producer/owner SHA or receipt mismatch")
        demand(owner.get("source_url", "").startswith("https://github.com/"),
               "historical owner source URL missing")
    demand(consumer.get("disposition") == "ACCEPT" and
           child.get("disposition") == "ACCEPT", "historical owner disposition")
    return {
        "status": "HISTORICAL_DOCUMENT_CROSSWALK_ONLY",
        "source_sha": sha, "run_id": producer["run_id"],
        "native_job_success_n": producer["workflow_jobs_success"],
        "native_job_denominator": producer["workflow_jobs_success"],
        "owner_documents_matched": 2, "owner_document_denominator": 2,
        "source_url": producer.get("source_url"),
        "legacy_reported_steps": producer.get("historical_steps_reported"),
        "strict_steps_comparable": False,
        "reason": "historical producer counted echoed commands and backtrace text; no current-head credit",
    }


def pulse_row(label: str, *, p1: str, p2: str, sha: str | None,
              cohort: str, run_id: int | None = None) -> dict:
    demand(p1 in TERMINAL | {"unknown"} and p2 in TERMINAL | {"unknown"},
           "unrecognized native job state")
    known = [p1, p2]
    success_n = sum(s == "success" for s in known)
    terminal_n = sum(s in TERMINAL for s in known)
    report = {
        "pulse": label, "cohort": cohort, "source_sha": sha,
        "run_id": run_id, "states": {"P1": p1.upper(), "P2": p2.upper()},
        "successful_jobs": success_n, "expected_jobs": 2,
        "terminal_jobs": terminal_n,
        "pass_fraction": {"numerator": success_n, "denominator": 2} if terminal_n == 2 else None,
        "reason": "NONTERMINAL" if terminal_n < 2 else "TERMINAL",
    }
    return report


def current_join(native: dict | None, *, sha: str, abacus: dict | None = None,
                 qps: dict | None = None) -> dict:
    """Report matching current owner payloads without assigning acceptance authority."""
    if native is None:
        return {"status": "DEFER_NO_CURRENT_PRODUCER_RECEIPT", "matched_owners": 0,
                "required_owners": 2, "owner_decision": "WITHHELD"}
    proof = verify_native(native, sha)
    matched = 0
    for repo, obj, sha_key, receipt_key, disposition_key in (
        (ABACUS, abacus, "producer_exact_head_sha", "producer_receipt_sha256", "current_disposition"),
        (QPS, qps, "producer_exact_head_sha", "producer_receipt_sha256", "current_child_disposition"),
    ):
        if obj is None:
            continue
        demand(isinstance(obj, dict) and obj.get("producer_repo") == CODEX, "owner wrong producer")
        demand(obj.get("consumer_repo" if repo == ABACUS else "child_repo") == repo, "owner wrong repository")
        demand(obj.get(sha_key) == sha and obj.get(receipt_key) == native["receipt_sha256"],
               "current owner exact-source/receipt mismatch")
        demand(obj.get(disposition_key) == "ACCEPT", "current owner does not accept")
        matched += 1
    return {"status": "CURRENT_OWNER_DOCUMENTS_BOUND" if matched == 2 else "DEFER_OWNER_RECEIPTS_PENDING",
            "matched_owners": matched, "required_owners": 2,
            "code_x_native_cli": proof["native_cli_probe"],
            "code_x_real_steps": proof["native_cli_steps"],
            "lldb_dap_live": "UNVERIFIED", "mcp_native": "UNVERIFIED",
            "docker_native": "UNVERIFIED", "qps_engineering_credit": 0,
            "owner_decision": "REFER_TO_QPS_OWNER" if matched == 2 else "WITHHELD"}


def produce(history: dict, *, sha: str, p1: str, p2: str,
            native: dict | None = None, run_id: int | None = None) -> dict:
    demand(SHA.fullmatch(sha) is not None, "current exact head")
    old = owner_history(history)
    if native is not None:
        demand(p1 == "success" and p2 == "success", "native success without successful jobs")
    joined = current_join(native, sha=sha)
    waves = [
        pulse_row("N-1", p1="success", p2="success", sha=old["source_sha"],
                  run_id=old["run_id"], cohort="HISTORICAL_LEGACY_PROBE"),
        pulse_row("N", p1="failure", p2="skipped", sha="fae6a123ee849893a3025d89d4249284b5b5977a",
                  run_id=39147816451, cohort="W1_SYNTHETIC_PR_MERGE_FIRST_RED"),
        pulse_row("N+1", p1=p1, p2=p2, sha=sha, run_id=run_id,
                  cohort="W2_SOURCE_HEAD_PINNED_REPAIR"),
    ]
    out = {
        "schema": SCHEMA, "created_utc": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "source_sha": sha, "run_id": run_id,
        "run_attempt": os.getenv("GITHUB_RUN_ATTEMPT"),
        "wave": "W2", "pulses": waves, "historical_owner_chain": old,
        "current_owner_chain": joined,
        "native_receipt_integrity": "LOCAL_BYTES_VERIFIED_NOT_GITHUB_ARCHIVE_DIGEST" if native else "UNKNOWN",
        "comparison_class": "NONCOMPARABLE_METHOD_AND_HEAD_CHANGE",
        "actionable_first_red": "SOURCE_CHECKOUT_MERGE_REF_MISMATCH_REPAIRED_CANDIDATE",
        "next_pulse": "P3_CODEX_KEB_TO_ABACUS_DOW_TO_QPS_TRIAGE_OWNER_READBACK",
        "merge_admission": "HOLD", "qps_engineering_credit_delta": 0,
        "root_closure_credit": 0, "remote_dispatch_authorized": False,
        "coverage_uplift": None, "owner_controls_qualified": False,
        "qps_current_acceptance": "UNVERIFIED",
    }
    return out


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    p.add_argument("--expected-head", required=True)
    p.add_argument("--history", type=Path, required=True)
    p.add_argument("--p1", required=True)
    p.add_argument("--p2", required=True)
    p.add_argument("--native-receipt", type=Path)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    head = checked_head(a.root, a.expected_head)
    hist = json.loads(a.history.read_text(encoding="utf-8"))
    receipt = json.loads(a.native_receipt.read_text(encoding="utf-8")) if a.native_receipt and a.native_receipt.is_file() else None
    run = os.environ.get("GITHUB_RUN_ID")
    result = produce(hist, sha=head, p1=a.p1, p2=a.p2, native=receipt,
                     run_id=int(run) if run and run.isdigit() else None)
    a.out.mkdir(parents=True, exist_ok=True)
    payload = (json.dumps(result, sort_keys=True, indent=2) + "\n").encode()
    (a.out / "p3-wave-observation.json").write_bytes(payload)
    (a.out / "sha256-manifest.json").write_text(json.dumps({
        "schema": "codepurple.swift.roof.p3.hash.v1", "source_sha": head,
        "p3_observation_sha256": hashlib.sha256(payload).hexdigest(),
        "gate": "HOLD", "authority_transfer": False}, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"source_sha":head,"owner_chain":result["current_owner_chain"]["status"],
                     "native_pulse":result["pulses"][2]["states"],"merge":"HOLD"},sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
