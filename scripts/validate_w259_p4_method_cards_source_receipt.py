#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "ssot/bridge_rows/gg_math_method_cards_w259_p4_source_receipt.json"

EXPECTED_BUNDLE = {
    "crew_blob": "41fd9210235d47819e580b7c25ef0ea384918d9a",
    "gg_math_cards_blob": "c9ae20146c8e92f2eb387b410a7a8c8256e661b2",
    "gg_math_graph_blob": "8cdecd4af9bf85c060138eebb40edce8033b6e12",
    "gg_math_merge": "0af77a081af76a0ac1244a953e0e5f27319b8276",
    "mission_control_blob": "24587c5525f88ca25a6977688e29c344d3471197",
    "mission_register_blob": "d35b0c1f53b6f35c91cadfb5b0e284459d06eedf",
    "missioncontrol_merge": "98686026c4fbc18be5d0ad9d458d37f55c3e7b36",
    "qps_cards_control_blob": "0cfc5987438f62f87f751586fbc519c2d614a44d",
    "qps_graph_control_blob": "7ac80b0f687c59b85d90f54cb233d580a3a0dcf5",
    "qps_w259r_merge": "28c5e44b835f53387f50900366edd1ca6811a9c9"
}
EXPECTED_DIGEST = "a5ea0c436bfb695245bed82a8275a5a775fea94cb3f8555e5cd89d44b5726012"
EXPECTED_THRESHOLD_KINDS = {
    "EXACT_IDENTITY", "DISTRIBUTION_DERIVED", "MODEL_DERIVED", "DATA_CALIBRATED",
    "HEURISTIC", "PROJECT_GOVERNED", "NO_UNIVERSAL_THRESHOLD", "RESEARCH_TODO"
}
EXPECTED_PLANES = {
    "P1": ("3PR", "METHOD_MATH"),
    "P2": ("MIP", "PROJECT_MATH_QPS"),
    "P3": ("3PC", "TRIAGE_GOVERNANCE"),
    "P4": ("3P3", "FEDERATION_ORCHESTRATION"),
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def bundle_digest() -> str:
    raw = json.dumps(EXPECTED_BUNDLE, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    checks: list[dict] = []

    def ok(name: str, condition: bool, detail: str = "") -> None:
        require(condition, f"{name}: {detail}")
        checks.append({"check": name, "result": "PASS", "detail": detail})

    ok("01_object_type", receipt["object_type"] == "KEB_SOURCE_RECEIPT")
    ok("02_item_id", receipt["keb_item_id"] == "KEB-ITEM-0003")
    ok("03_provider_merge", receipt["source_sha"] == EXPECTED_BUNDLE["gg_math_merge"])
    ok("04_bundle_digest_recomputed", bundle_digest() == EXPECTED_DIGEST, bundle_digest())
    ok("05_receipt_digest", receipt["source_digest"] == f"sha256:{EXPECTED_DIGEST}")
    ok("06_card_count", receipt["bundle"]["gg_math"]["card_count"] == 16)
    ok("07_threshold_kinds", set(receipt["bundle"]["gg_math"]["threshold_kinds"]) == EXPECTED_THRESHOLD_KINDS)
    ok("08_missioncontrol_merge", receipt["bundle"]["mission_control"]["merge_sha"] == EXPECTED_BUNDLE["missioncontrol_merge"])
    ok("09_qps_merge", receipt["bundle"]["qps"]["w259r_merge_sha"] == EXPECTED_BUNDLE["qps_w259r_merge"])
    for pulse, (operator, plane) in EXPECTED_PLANES.items():
        row = receipt["transaction_semantics"][pulse]
        ok(f"10_{pulse}_operator_plane", row["operator"] == operator and row["plane"] == plane)
    guards = receipt["authority_guards"]
    ok("14_no_authority_transfer", guards["authority_transfer"] is False)
    ok("15_no_gate_compensation", guards["hard_gate_compensation_allowed"] is False)
    ok("16_zero_formal_credit", guards["formal_engineering_credit_delta"] == 0)
    ok("17_zero_negotiation_credit", guards["negotiation_credit_delta"] == 0)
    ok("18_no_runtime_gold", guards["runtime_gold_created"] is False)
    ok("19_no_release_authority", guards["release_authority_created"] is False)
    anti = receipt["anti_inference_guards"]
    ok("20_anti_inference_all_false", all(value is False for value in anti.values()))

    result = {
        "schema": "codex.w259.p4.keb_source_validation.v1",
        "result": "PASS_W259_P4_KEB_SOURCE_RECEIPT",
        "check_count": len(checks),
        "checks": checks,
        "canonical_bundle_digest": f"sha256:{EXPECTED_DIGEST}",
        "downstream": "GBOGEB/ABACUS/DOW",
        "authority_transfer": False,
        "formal_credit_delta": 0,
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
