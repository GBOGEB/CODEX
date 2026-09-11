#!/usr/bin/env python3
"""Normalize a W111 ABACUS/DOW analytical receipt for QPS child re-entry.

CODEX may validate semantics/provenance and wrap the DOW finding, but it may not
change analytical numeric values or promote QPS engineering state.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DOW = ROOT / "triage" / "returns" / "DOW_W111_POWER_UTILITY_RECEIPT.json"
EXPECTED_PAYLOAD_SHA256 = "cb66708b29a57abd8cd2721e40706a114f74e1941c1692af8c465370d96e124b"
EXPECTED_CHILD_SSOT_BLOB = "d19975a150a3530cc4db3bd2fbbf4180f757c2a4"


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must be a JSON object")
    return value


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def normalize(dow: dict, dow_file_sha256: str) -> dict:
    require(dow.get("authority_scope") == "REPO_LOCAL_ANALYTICAL_RUNTIME", "DOW authority scope mismatch")
    require(dow.get("engineering_promotion_forbidden") is True, "DOW promotion guard missing")
    source = dow.get("source_contract", {})
    require(source.get("source_ssot_git_blob_sha") == EXPECTED_CHILD_SSOT_BLOB, "child SSOT identity mismatch")
    require(source.get("input_payload_sha256") == EXPECTED_PAYLOAD_SHA256, "DOW input payload digest mismatch")
    require(source.get("payload_digest_verified") is True, "DOW payload verification missing")
    require(source.get("keb_receipt_verified") is True, "DOW did not verify KEB receipt")
    require(source.get("coolprop_receipt_verified") is True, "DOW did not verify CoolProp receipt")

    inv = dow.get("invCOP_screen", {})
    require(abs(float(inv.get("unreconciled_electrical_kW")) - 153.13) < 1e-6, "DOW residual changed")
    require(inv.get("residual_classification") == "SOURCE_GAP_NOT_BASELOAD", "DOW residual semantic changed")
    require(dow.get("baseload", {}).get("status") == "DEFER_NOT_IDENTIFIED", "baseload must remain DEFER")
    require("DEFER" in str(dow.get("pca", {}).get("status", "")), "PCA must remain deferred for inadequate sample")

    cross = dow.get("independent_thermophysical_crosscheck", {})
    require(abs(float(cross.get("isothermal_relative_delta"))) < 0.001, "CoolProp isothermal crosscheck outside tolerance")
    require(abs(float(cross.get("isentropic_reference_relative_delta"))) < 0.001, "CoolProp isentropic reference crosscheck outside tolerance")

    return {
        "schema": "codex-keb-w111-dow-return/0.1",
        "receipt_id": "KEB-W111-POWER-UTILITY-RETURN",
        "authority_scope": "REPO_LOCAL_SEMANTIC_RUNTIME",
        "engineering_promotion_forbidden": True,
        "child_action_required": "ACCEPT_REJECT_OR_DEFER",
        "child_source_ssot_git_blob_sha": EXPECTED_CHILD_SSOT_BLOB,
        "input_payload_sha256": EXPECTED_PAYLOAD_SHA256,
        "output_payload_sha256": EXPECTED_PAYLOAD_SHA256,
        "payload_digest_preserved": True,
        "dow_receipt_file_sha256": dow_file_sha256,
        "semantic_normalization": "PASS_NO_NUMERIC_MUTATION",
        "source_gap_disposition_candidate": "DEFER_SOURCE_GAPS",
        "preserved_findings": {
            "compression_points": dow.get("compression_points"),
            "independent_thermophysical_crosscheck": cross,
            "invCOP_screen": inv,
            "baseload": dow.get("baseload"),
            "pca": dow.get("pca"),
            "next_BG": dow.get("next_BG"),
            "next_CG": dow.get("next_CG"),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=str(DEFAULT_DOW))
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    inp = Path(args.input)
    dow = load_json(inp)
    result = normalize(dow, file_sha256(inp))
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("QPS_W111_KEB_DOW_RETURN_NORMALIZATION=PASS")
    print(f"payload_sha256={EXPECTED_PAYLOAD_SHA256}")
    print(f"dow_receipt_sha256={result['dow_receipt_file_sha256']}")
    print("numeric_mutation=false")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print("QPS_W111_KEB_DOW_RETURN_NORMALIZATION=FAIL", file=sys.stderr)
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
