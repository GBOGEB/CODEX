#!/usr/bin/env python3
"""Bind QPS debug runtime evidence into CODEX/KEB without inventing truth.

Two evidence modes are explicit and intentionally non-interchangeable:
- QPS_REPO_LOCAL: original QPS envelope with recursive-audit evidence.
- FEDERATED_EXACT_PAYLOAD: exact QPS target bytes executed on a healthy
  federated runner, requiring exact source SHA, payload hash, real LLDB steps,
  and adapter readiness while the QPS repo-local runner gate stays withheld.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "runtime" / "debug" / "generated"


def load_json(path: Path | None, env_name: str) -> dict | None:
    if path and path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    raw = os.getenv(env_name)
    if raw:
        return json.loads(raw)
    return None


def evaluate_repo_local(envelope: dict) -> dict:
    valid_producer = envelope.get("producer") == "GBOGEB/cryoplant-project"
    producer_accept = envelope.get("status") == "ACCEPT"
    exact_sha = envelope.get("exact_head_sha")
    minimum = envelope.get("minimum_victory_condition", {})
    steps = bool(minimum.get("runtime_steps_gt_zero"))
    audit = bool(minimum.get("recursive_audit_pass"))
    accept = bool(
        valid_producer
        and producer_accept
        and exact_sha
        and exact_sha != "UNKNOWN"
        and steps
        and audit
    )
    return {
        "mode": "QPS_REPO_LOCAL",
        "accept": accept,
        "exact_sha": exact_sha,
        "source_receipt_sha256": envelope.get("envelope_sha256"),
        "checks": {
            "producer_identity_valid": valid_producer,
            "producer_status_accept": producer_accept,
            "exact_head_sha_present": bool(exact_sha and exact_sha != "UNKNOWN"),
            "runtime_steps_gt_zero": steps,
            "recursive_audit_pass": audit,
            "source_payload_hash_match": None,
            "adapter_surface_ready": None,
            "repo_local_runner_recovered": True,
        },
    }


def evaluate_federated(receipt: dict) -> dict:
    source = receipt.get("source", {})
    execution = receipt.get("execution", {})
    adapter = receipt.get("adapter", {})
    guards = receipt.get("authority_guards", {})
    source_repo_ok = source.get("repository") == "GBOGEB/cryoplant-project"
    exact_sha = source.get("exact_sha")
    payload_hash = bool(source.get("payload_hash_match"))
    steps = (execution.get("real_probe_steps") or 0) > 0
    exec_accept = execution.get("probe_status") == "ACCEPT"
    dov_pass = execution.get("dov_status") == "PASS"
    adapter_ready = bool(
        adapter.get("surface_present")
        and adapter.get("surface_state") == "READY"
        and adapter.get("surface_probe_returncode") == 0
    )
    local_gate_separate = guards.get("qps_repo_local_runner_gate") == "WITHHELD_EXTERNAL"
    accept = bool(
        source_repo_ok
        and exact_sha
        and exact_sha != "UNKNOWN"
        and payload_hash
        and steps
        and exec_accept
        and dov_pass
        and adapter_ready
        and local_gate_separate
    )
    return {
        "mode": "FEDERATED_EXACT_PAYLOAD",
        "accept": accept,
        "exact_sha": exact_sha,
        "source_receipt_sha256": receipt.get("original_receipt_sha256"),
        "checks": {
            "producer_identity_valid": source_repo_ok,
            "producer_status_accept": exec_accept and dov_pass,
            "exact_head_sha_present": bool(exact_sha and exact_sha != "UNKNOWN"),
            "runtime_steps_gt_zero": steps,
            "recursive_audit_pass": None,
            "source_payload_hash_match": payload_hash,
            "adapter_surface_ready": adapter_ready,
            "repo_local_runner_recovered": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--envelope", type=Path)
    group.add_argument("--federated-receipt", type=Path)
    args = parser.parse_args()

    federated = load_json(args.federated_receipt, "QPS_FEDERATED_DEBUG_RECEIPT_JSON")
    envelope = load_json(args.envelope, "QPS_DEBUG_ENVELOPE_JSON")

    if federated:
        result = evaluate_federated(federated)
    elif envelope:
        result = evaluate_repo_local(envelope)
    else:
        result = {
            "mode": "NONE",
            "accept": False,
            "exact_sha": None,
            "source_receipt_sha256": None,
            "checks": {
                "producer_identity_valid": False,
                "producer_status_accept": False,
                "exact_head_sha_present": False,
                "runtime_steps_gt_zero": False,
                "recursive_audit_pass": False,
                "source_payload_hash_match": False,
                "adapter_surface_ready": False,
                "repo_local_runner_recovered": False,
            },
        }

    accept = bool(result["accept"])
    mode = result["mode"]
    binding = {
        "schema": "codex.keb.qps_debug_binding.v2",
        "binding_id": "KEB-QPS-DEBUG-DAG-001",
        "created_utc": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "semantic_owner": "CODEX/KEB",
        "producer": "GBOGEB/cryoplant-project",
        "producer_exact_head_sha": result["exact_sha"],
        "evidence_mode": mode,
        "status": "ACCEPT" if accept else "DEFER",
        "reason": (
            f"{mode}_RUNTIME_EVIDENCE_ACCEPT"
            if accept
            else f"{mode}_RUNTIME_EVIDENCE_NOT_ACCEPTABLE_OR_ABSENT"
        ),
        "source_receipt_sha256": result["source_receipt_sha256"],
        "checks": result["checks"],
        "authority_guards": {
            "engineering_authority_transfer": False,
            "formal_engineering_credit_delta": 0,
            "negotiation_credit_delta": 0,
            "keb_binding_is_runtime_evidence_only": True,
            "federated_mode_does_not_claim_repo_local_runner_recovery": True,
        },
    }
    binding["binding_sha256"] = hashlib.sha256(
        json.dumps(binding, sort_keys=True).encode()
    ).hexdigest()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "qps_debug_keb_binding.json").write_text(
        json.dumps(binding, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(binding, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
