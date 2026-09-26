#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from ruamel.yaml import YAML

ROOT = Path(__file__).resolve().parents[1]
BRIDGE = ROOT / "triage/GM_I_A_COOLPROP_FAST_HEAVY_KEB_BRIDGE.yaml"
EXPECTED_DIGEST = "4c32dca1a3f60b3b587d159702880a3c5c5987e878ebc228063650533c084ea6"
EXPECTED_SOURCE = "a88d6e8cc24402868afab39a71fc49fcacec08c8"
EXPECTED_MERGE = "e31433c4427be2aaad064294e6c6cab1843537df"
EXPECTED_RUN = 36226071145


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def load_bridge() -> dict:
    bridge = YAML(typ="safe").load(BRIDGE.read_text(encoding="utf-8")) or {}
    require(bridge.get("schema") == "codex.gm_i_a_coolprop_fast_heavy_keb_bridge.v1", "bridge schema mismatch")
    require(bridge.get("mission") == "GM-I-A", "bridge mission mismatch")
    consumer = bridge.get("consumer") or {}
    require(consumer.get("repo") == "GBOGEB/CODEX", "consumer repo mismatch")
    require(consumer.get("authority_transfer") is False, "bridge authority transfer must remain false")
    require(consumer.get("formal_credit_delta") == 0, "bridge formal credit must remain zero")
    atom = bridge.get("knowledge_atom") or {}
    require(atom.get("object_type") == "KEB_KNOWLEDGE_ATOM_CANDIDATE", "bridge must remain candidate-only")
    require(atom.get("promotion") == "NON_ENGINEERING_REFERENCE_ONLY", "candidate promotion boundary mismatch")
    return bridge


def validate_provider(d: dict) -> None:
    require(d.get("schema") == "qps.gm_i_a.fast_heavy.federation_attestation.v1", "provider schema mismatch")
    require(d.get("mission") == "GM-I-A", "provider mission mismatch")
    require(d.get("lane") == "L9_FEDERATION", "provider lane mismatch")
    require(d.get("source_head_sha") == EXPECTED_SOURCE, "provider source head mismatch")
    require(d.get("source_merge_sha") == EXPECTED_MERGE, "provider source merge mismatch")
    workflow = d.get("workflow") or {}
    require(workflow.get("run_id") == EXPECTED_RUN, "provider run mismatch")
    require(workflow.get("conclusion") == "success", "provider workflow did not succeed")
    heavy = d.get("heavy") or {}
    require(heavy.get("conclusion") == "success", "heavy lane did not succeed")
    require(float(heavy.get("build_seconds", 0)) > 0, "heavy build seconds missing")
    fast = d.get("fast") or {}
    require(fast.get("conclusion") == "success", "fast lane did not succeed")
    require(int(fast.get("calculations_passed", 0)) > 0, "fast calculations missing")
    require(fast.get("build_invoked") is False, "fast lane unexpectedly built source")
    require(fast.get("source_checkout_performed") is False, "fast lane unexpectedly checked out source")
    economics = d.get("runtime_economics") or {}
    require(economics.get("fast_execution_is_independent_of_source_build") is True, "runtime economics boundary mismatch")
    authority = d.get("authority") or {}
    require(authority.get("scope") == "COMPATIBILITY_RUNTIME_ONLY", "provider authority scope mismatch")
    require(authority.get("authority_transfer") is False, "provider authority transfer must remain false")
    require(authority.get("engineering_promotion") == "WITHHELD", "provider engineering promotion must remain withheld")


def build_receipt(d: dict, digest: str, bridge: dict) -> dict:
    atom = bridge["knowledge_atom"]
    return {
        "schema": "codex.keb.gm_i_a.fast_heavy.v1",
        "object_type": atom["object_type"],
        "status": "PASS_VALIDATED_CANDIDATE",
        "promotion_state": atom["promotion"],
        "canonical_keb_atom": False,
        "promotion_evidence_present": False,
        "provider_repo": d["provider_repo"],
        "provider_attestation_commit": "0b5147156e949a17ca1b4f01ea5cc5067c9628ed",
        "provider_attestation_sha256": digest,
        "provider_source_head_sha": d["source_head_sha"],
        "provider_runtime_run_id": d["workflow"]["run_id"],
        "knowledge": {
            "topic": "FAST_HEAVY_RUNTIME_ECONOMICS",
            "heavy_build_seconds": d["heavy"]["build_seconds"],
            "heavy_queue_seconds": d["heavy"]["queue_seconds"],
            "fast_execute_seconds": d["fast"]["execute_seconds"],
            "fast_queue_seconds": d["fast"]["queue_seconds"],
            "fast_calculations_passed": d["fast"]["calculations_passed"],
            "observation": "BUILD_AND_RUNNER_QUEUE_ARE_DISTINCT_RUNTIME_PRESSURES",
        },
        "authority_scope": "NON_ENGINEERING_REFERENCE_ONLY",
        "authority_transfer": False,
        "formal_credit_delta": 0,
        "engineering_promotion_forbidden": True,
        "abacus_bridge_compensation_forbidden": True,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--provider", required=True)
    ap.add_argument("--receipt", required=True)
    args = ap.parse_args()

    provider = Path(args.provider)
    digest = hashlib.sha256(provider.read_bytes()).hexdigest()
    require(digest == EXPECTED_DIGEST, f"provider digest mismatch: {digest}")
    data = json.loads(provider.read_text(encoding="utf-8"))
    validate_provider(data)
    bridge = load_bridge()
    out = build_receipt(data, digest, bridge)
    Path(args.receipt).write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
