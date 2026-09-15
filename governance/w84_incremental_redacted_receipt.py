#!/usr/bin/env python3
"""Validate a privacy-safe W84 child source receipt.

Public parent repositories validate child lineage and source-binding assertions
without copying private bidder source locators, source hashes, or numerical values.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ALLOWED_ATOMS = {
    "LB-01-PLOC", "LB-02-BFLOW", "LB-03-GEO-A", "LB-04-GEO-B",
    "LB-05-THERM-A", "LB-06-THERM-B",
}
FORBIDDEN_PRIVATE_FIELDS = {
    "source_locator", "source_sha256", "value_g_s", "governing_requirement_g_s_min",
}


def _hex(value: str, length: int) -> bool:
    return len(value) == length and all(c in "0123456789abcdef" for c in value.lower())


def validate(receipt: dict) -> dict:
    forbidden_present = sorted(FORBIDDEN_PRIVATE_FIELDS.intersection(receipt))
    passed = all(
        [
            receipt.get("child_repo") == "GBOGEB/cryoplant-project",
            _hex(str(receipt.get("child_commit_sha", "")), 40),
            receipt.get("atom_id") in ALLOWED_ATOMS,
            _hex(str(receipt.get("child_gate_digest_sha256", "")), 64),
            _hex(str(receipt.get("child_package_digest_sha256", "")), 64),
            receipt.get("source_locator_present") is True,
            receipt.get("source_sha256_valid") is True,
            receipt.get("child_atom_eligible") is True,
            not forbidden_present,
        ]
    )
    return {
        "wave": "W84",
        "plane": "KEB",
        "atom_id": receipt.get("atom_id"),
        "incremental_semantic_provenance_pass": passed,
        "private_fields_copied": forbidden_present,
        "required_action": "ROUNDTRIP_ATOM_TO_DOW" if passed else "RETURN_TO_CHILD_SOURCE_RECOVERY",
        "engineering_credit_delta": 0,
        "authority": "NON_PROMOTING_PARENT_RETURN",
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("receipt", type=Path)
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    result = validate(json.loads(args.receipt.read_text(encoding="utf-8")))
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0 if result["incremental_semantic_provenance_pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
