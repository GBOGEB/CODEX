#!/usr/bin/env python3
"""Fail-closed validator and receipt emitter for the W111 QPS KEB bridge."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "triage" / "W111_QPS_POWER_UTILITY_KEB_BRIDGE.yaml"
PAYLOAD = ROOT / "triage" / "payloads" / "QPS_W111_POWER_UTILITY_SANITIZED_v1.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def canonical_payload_sha256(body: dict) -> str:
    encoded = json.dumps(
        body,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def atom_map(body: dict) -> dict[str, dict]:
    return {str(atom["id"]): atom for atom in body.get("atoms", [])}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipt")
    args = parser.parse_args()

    data = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    require(isinstance(data, dict), "manifest must be a mapping")
    require(data.get("repo") == "GBOGEB/CODEX", "CODEX repo identity mismatch")
    require(
        data.get("authority_scope") == "REPO_LOCAL_SEMANTIC_RUNTIME",
        "invalid authority scope",
    )
    require(
        data.get("engineering_promotion_forbidden") is True,
        "QPS promotion must be forbidden in CODEX",
    )

    child = data.get("qps_child_authority", {})
    require(child.get("repo") == "GBOGEB/cryoplant-project", "child authority repo mismatch")
    require(
        child.get("source_ssot")
        == "ocd-adr/20_canonical/control/QPS_W111_POWER_UTILITY_SOURCE_SSOT_v1.json",
        "wrong W111 source SSOT",
    )
    require(
        len(str(child.get("source_ssot_git_blob_sha", ""))) == 40,
        "child source SSOT git blob SHA required",
    )

    taxonomy = data.get("semantic_taxonomy", {})
    require(
        set(taxonomy.get("electrical_boundary", {}))
        == {"E0", "E1", "E2", "E3", "E4"},
        "E0-E4 boundary incomplete",
    )
    require(
        set(taxonomy.get("thermal_boundary", {}))
        == {"T0", "T1", "T2", "T3", "T4", "T5"},
        "E0-E4/T0-T5 boundary incomplete",
    )

    inv = set(data.get("hard_invariants", []))
    for marker in (
        "stale_52p4Hz_interpolation_is_rejected",
        "unknown_auxiliary_HVAC_UPS_fan_or_pump_load_is_not_zero",
        "315kW_motor_rating_is_not_357kW_package_input",
        "returned_cold_must_be_accounted_once_across_a_declared_control_volume",
        "derived_MC_PCA_BT_outputs_never_promote_QPS_state",
    ):
        require(marker in inv, f"missing invariant: {marker}")

    envelope = json.loads(PAYLOAD.read_text(encoding="utf-8"))
    body = envelope.get("payload_body")
    require(isinstance(body, dict), "payload_body must be a mapping")
    calculated_digest = canonical_payload_sha256(body)
    declared_digest = str(envelope.get("payload_sha256", ""))
    require(calculated_digest == declared_digest, "payload SHA256 mismatch")
    require(
        declared_digest
        == "cb66708b29a57abd8cd2721e40706a114f74e1941c1692af8c465370d96e124b",
        "unexpected W111 payload digest",
    )

    payload_authority = body.get("authority", {})
    require(
        payload_authority.get("source_ssot_git_blob_sha")
        == child.get("source_ssot_git_blob_sha"),
        "payload source SSOT blob differs from KEB contract",
    )
    confidentiality = body.get("confidentiality", {})
    for forbidden_flag in (
        "raw_bidder_pdf_included",
        "raw_offer_text_included",
        "commercial_price_table_included",
    ):
        require(confidentiality.get(forbidden_flag) is False, f"forbidden payload: {forbidden_flag}")

    atoms = atom_map(body)
    require(atoms["LKT_HP_FREQUENCY_2KOP"]["value"] == 56.0, "56 Hz immutable regression")
    require(atoms["LKT_HP_TOTAL_FLOW_2KOP"]["value"] == 326.0, "326 g/s regression")
    require(atoms["LKT_HP_FLOW_EACH_2KOP"]["value"] == 81.5, "81.5 g/s regression")
    require(atoms["LKT_HP_P1"]["value"] == 1.05, "HP P1 regression")
    require(atoms["LKT_HP_P2"]["value"] == 14.0, "HP P2 regression")
    require(
        atoms["LKT_UNRECONCILED_ELECTRICAL"]["evidence_class"] == "UNKNOWN",
        "153.13 kW residual must remain UNKNOWN",
    )

    receipt = {
        "schema": "codex-keb-w111-power-utility-receipt/0.1",
        "receipt_id": "KEB-W111-POWER-UTILITY",
        "authority_scope": "REPO_LOCAL_SEMANTIC_RUNTIME",
        "engineering_promotion_forbidden": True,
        "child_source_ssot_git_blob_sha": child["source_ssot_git_blob_sha"],
        "input_payload_sha256": declared_digest,
        "output_payload_sha256": declared_digest,
        "payload_digest_preserved": True,
        "semantic_checks": "PASS",
        "provenance_checks": "PASS",
        "confidentiality_checks": "PASS",
        "dispatch_target": "GBOGEB/ABACUS",
        "child_return_required": True,
    }
    if args.receipt:
        out = Path(args.receipt)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print("QPS_W111_KEB_BRIDGE_VALIDATION=PASS")
    print(f"payload_sha256={declared_digest}")
    print("payload_digest_preserved=true")
    print("engineering_promotion_forbidden=true")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print("QPS_W111_KEB_BRIDGE_VALIDATION=FAIL", file=sys.stderr)
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
