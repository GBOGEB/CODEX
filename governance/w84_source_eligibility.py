#!/usr/bin/env python3
"""CODEX/KEB W84 provenance eligibility validator.

Consumes a child source package and emits a non-promoting KEB receipt. Eligibility
requires exact source locators and SHA-256 values for all six Line-B atoms.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

REQUIRED = {
    "LB-01-PLOC", "LB-02-BFLOW", "LB-03-GEO-A", "LB-04-GEO-B",
    "LB-05-THERM-A", "LB-06-THERM-B",
}


def valid_hash(value: str) -> bool:
    return len(value) == 64 and all(c in "0123456789abcdef" for c in value.lower())


def validate(payload: dict) -> dict:
    atoms = {a.get("atom_id"): a for a in payload.get("atoms", [])}
    findings = []
    for atom_id in sorted(REQUIRED):
        atom = atoms.get(atom_id, {})
        locator = str(atom.get("source_locator", "")).strip()
        digest = str(atom.get("source_sha256", "")).strip().lower()
        state = atom.get("state", "MISSING")
        eligible = state == "ACCEPTED_SOURCE_BOUND" and bool(locator) and valid_hash(digest)
        findings.append({
            "atom_id": atom_id,
            "eligible": eligible,
            "state": state,
            "locator_present": bool(locator),
            "sha256_valid": valid_hash(digest),
        })
    passed = all(f["eligible"] for f in findings)
    payload_bytes = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return {
        "wave": "W84",
        "plane": "KEB",
        "source_package_sha256": hashlib.sha256(payload_bytes).hexdigest(),
        "semantic_provenance_pass": passed,
        "findings": findings,
        "required_child_action": "ROUNDTRIP_TO_DOW" if passed else "REMAIN_SOURCE_RECOVERY",
        "engineering_credit_delta": 0,
        "guards": [
            "page_binding_is_not_compliance_credit",
            "historic_evidence_is_not_current_authority",
            "parent_return_is_not_child_authority",
            "cross_bidder_substitution_forbidden",
        ],
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("package", type=Path)
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    receipt = validate(json.loads(args.package.read_text(encoding="utf-8")))
    text = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0 if receipt["semantic_provenance_pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
