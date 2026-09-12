#!/usr/bin/env python3
"""Consume a QPS debug federation envelope into CODEX/KEB without inventing runtime truth."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "runtime" / "debug" / "generated"


def load_envelope(path: Path | None) -> dict | None:
    if path and path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    raw = os.getenv("QPS_DEBUG_ENVELOPE_JSON")
    if raw:
        return json.loads(raw)
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--envelope", type=Path)
    args = parser.parse_args()
    envelope = load_envelope(args.envelope)

    valid_producer = bool(envelope and envelope.get("producer") == "GBOGEB/cryoplant-project")
    producer_accept = bool(envelope and envelope.get("status") == "ACCEPT")
    exact_sha = envelope.get("exact_head_sha") if envelope else None
    steps = bool(envelope and envelope.get("minimum_victory_condition", {}).get("runtime_steps_gt_zero"))
    audit = bool(envelope and envelope.get("minimum_victory_condition", {}).get("recursive_audit_pass"))
    accept = bool(valid_producer and producer_accept and exact_sha and exact_sha != "UNKNOWN" and steps and audit)

    binding = {
        "schema": "codex.keb.qps_debug_binding.v1",
        "binding_id": "KEB-QPS-DEBUG-DAG-001",
        "created_utc": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "semantic_owner": "CODEX/KEB",
        "producer": "GBOGEB/cryoplant-project",
        "producer_exact_head_sha": exact_sha,
        "status": "ACCEPT" if accept else "DEFER",
        "reason": "QPS_EXACT_HEAD_RUNTIME_ENVELOPE_ACCEPT" if accept else "QPS_EXACT_HEAD_RUNTIME_ENVELOPE_NOT_ACCEPTABLE_OR_ABSENT",
        "source_envelope_sha256": envelope.get("envelope_sha256") if envelope else None,
        "checks": {
            "producer_identity_valid": valid_producer,
            "producer_status_accept": producer_accept,
            "exact_head_sha_present": bool(exact_sha and exact_sha != "UNKNOWN"),
            "runtime_steps_gt_zero": steps,
            "recursive_audit_pass": audit,
        },
        "authority_guards": {
            "engineering_authority_transfer": False,
            "formal_engineering_credit_delta": 0,
            "negotiation_credit_delta": 0,
            "keb_binding_is_runtime_evidence_only": True,
        },
    }
    binding["binding_sha256"] = hashlib.sha256(json.dumps(binding, sort_keys=True).encode()).hexdigest()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "qps_debug_keb_binding.json").write_text(json.dumps(binding, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(binding, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
