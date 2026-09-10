#!/usr/bin/env python3
"""Validate the W101 immutable QPS input stage without regenerating any artifact."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

EXPECTED = {
    "QPS_OFFER_Cluster_v3_4_BT_RTM_Standards_Evidence.xlsx": "00a5f0ed3ded00620a33edd045706ba5fb9a67b5fb7fe63c495305f911c43ccb",
    "QPS_ALAT_SSOT_CURRENT_2026-09-07.xlsx": "5c4c845f7e9d88c1bfe002817c98e5584135cc8bc85bf9ea6596c183318a1907",
    "QPS_LKT_NEG_RFI_REVIEW_MASTER_W21_2.xlsx": "6d763cce948a1ee14c30c42b0367226f97dc4712beb6ab4b6e641ad0e8b00f3f",
    "QPS_LKT_ALAT_RTM_COMPLIANCE_W22L_RETURN_PACKAGES.xlsx": "b745ef62417d921495bffdc3154e8fc0340216d4ba7ad85e847a0b468a5327e4",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> int:
    stage = Path(sys.argv[1] if len(sys.argv) > 1 else "immutable-inputs")
    result = {
        "schema": "w101-immutable-stage-receipt/v1",
        "stage": str(stage),
        "policy": "VERIFY_ONLY_DO_NOT_REGENERATE",
        "files": {},
    }
    passed = 0
    for name, expected in EXPECTED.items():
        path = stage / name
        if not path.is_file():
            result["files"][name] = {"state": "MISSING", "expected_sha256": expected}
            continue
        actual = sha256(path)
        state = "PASS_EXACT_SHA256" if actual == expected else "HASH_MISMATCH"
        result["files"][name] = {
            "state": state,
            "expected_sha256": expected,
            "actual_sha256": actual,
            "bytes": path.stat().st_size,
        }
        passed += state == "PASS_EXACT_SHA256"

    result["passed"] = passed
    result["required"] = len(EXPECTED)
    result["status"] = "PASS_4_OF_4_IMMUTABLE_INPUTS" if passed == len(EXPECTED) else "DEFER_IMMUTABLE_INPUT_STAGE"
    Path("out").mkdir(exist_ok=True)
    receipt = Path("out/W101_IMMUTABLE_STAGE_RECEIPT.json")
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))
    return 0 if passed == len(EXPECTED) else 3


if __name__ == "__main__":
    raise SystemExit(main())
