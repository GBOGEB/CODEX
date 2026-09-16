#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ATOM = ROOT / "ssot/bridge_rows/gg_math_method_cards_w259_p4_knowledge_atom.json"
SOURCE = ROOT / "ssot/bridge_rows/gg_math_method_cards_w259_p4_source_receipt.json"

EXPECTED_BUNDLE = "sha256:a5ea0c436bfb695245bed82a8275a5a775fea94cb3f8555e5cd89d44b5726012"
EXPECTED_DOW_MERGE = "dcfac8f55cd48e163d6a051d3c7e7d254091b15c"
EXPECTED_DOW_ARTIFACT = "sha256:de404e21e5e7a36c4a5189606373429e8d0592841ac884607fa63d5cdd769aea"
EXPECTED_THRESHOLD_KINDS = {
    "EXACT_IDENTITY", "DISTRIBUTION_DERIVED", "MODEL_DERIVED", "DATA_CALIBRATED",
    "HEURISTIC", "PROJECT_GOVERNED", "NO_UNIVERSAL_THRESHOLD", "RESEARCH_TODO",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    atom = json.loads(ATOM.read_text(encoding="utf-8"))
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    checks: list[dict] = []

    def ok(name: str, condition: bool, detail: str = "") -> None:
        require(condition, f"{name}: {detail}")
        checks.append({"check": name, "result": "PASS", "detail": detail})

    ok("01_atom_type", atom["object_type"] == "KEB_KNOWLEDGE_ATOM")
    ok("02_atom_id", atom["keb_item_id"] == "KEB-ITEM-0004")
    ok("03_source_receipt_id", source["keb_item_id"] == "KEB-ITEM-0003" and source["object_type"] == "KEB_SOURCE_RECEIPT")
    ok("04_bundle_digest", atom["source_digest"] == source["source_digest"] == EXPECTED_BUNDLE)
    ok("05_provider_merge", atom["provider"]["merge_sha"] == source["bundle"]["gg_math"]["merge_sha"])
    ok("06_missioncontrol_merge", atom["mission_control"]["merge_sha"] == source["bundle"]["mission_control"]["merge_sha"])
    ok("07_qps_w259r_merge", atom["qps_pinning"]["w259r_merge"] == source["bundle"]["qps"]["w259r_merge_sha"])
    ok("08_keb_source_merge", atom["keb_source_binding"]["merge_sha"] == "d41e709c93d8c73ba392478592dd75627743a2ad")
    dow = atom["independent_dow_challenge"]
    ok("09_dow_merge", dow["merge_sha"] == EXPECTED_DOW_MERGE)
    ok("10_dow_artifact", dow["artifact_digest"] == EXPECTED_DOW_ARTIFACT)
    ok("11_dow_exact_run", dow["workflow_run_id"] == 35148942332 and dow["workflow_job_id"] == 104972030372 and dow["runner_id"] > 0)
    ok("12_dow_independent", dow["imports_gg_math"] is False and dow["imports_codex_runtime"] is False)
    ok("13_dow_parity", dow["semantic_parity"] == dow["threshold_kind_parity"] == dow["plane_mapping_parity"] == 1.0)
    ok("14_zero_authority_inversion", dow["authority_inversion_count"] == 0)
    claims = atom["knowledge_claims"]
    ok("15_card_count", claims["method_card_count"] == 16)
    ok("16_threshold_kinds", set(claims["threshold_kinds"]) == EXPECTED_THRESHOLD_KINDS)
    ok("17_ci_levels", claims["ci_canonical_levels"] == [90, 95, 99])
    ok("18_bt_parity", claims["bt_parity_probability"] == 0.5)
    ok("19_pca_sign_guard", claims["pca_sign_requires_alignment_before_interpretation"] is True)
    ok("20_project_threshold_guard", claims["project_governed_threshold_is_read_only_to_provider"] is True)
    ok("21_research_zero_authority", claims["research_todo_has_zero_consumer_authority"] is True)
    expected_planes = {
        "P1": ("3PR", "METHOD_MATH"),
        "P2": ("MIP", "PROJECT_MATH_QPS"),
        "P3": ("3PC", "TRIAGE_GOVERNANCE"),
        "P4": ("3P3", "FEDERATION_ORCHESTRATION"),
    }
    for pulse, (operator, plane) in expected_planes.items():
        row = atom["plane_contract"][pulse]
        ok(f"22_{pulse}_plane", row["operator"] == operator and row["plane"] == plane)
    ok("26_p4_optional", atom["plane_contract"]["P4"]["optional_cross_repo_or_authority_only"] is True)
    p4 = atom["p4_disposition"]
    ok("27_p4_control", p4 == {
        "Preserve_Pin": "PASS",
        "Propagate_Penetrate": "PASS_KEB_AND_DOW",
        "Prove_Promote": "PASS_KEB_KNOWLEDGE_ONLY",
        "domain_authority_created": False,
    })
    guards = atom["authority_guards"]
    ok("28_authority_guards", guards == {
        "authority_transfer": False,
        "hard_gate_compensation_allowed": False,
        "formal_engineering_credit_delta": 0,
        "negotiation_credit_delta": 0,
        "engineering_acceptance_created": False,
        "compliance_acceptance_created": False,
        "runtime_gold_created": False,
        "release_authority_created": False,
        "issue_923_compensated": False,
    })

    result = {
        "schema": "codex.w259.p4.keb_knowledge_atom_validation.v1",
        "result": "PASS_W259_P4_KEB_KNOWLEDGE_ATOM",
        "check_count": len(checks),
        "checks": checks,
        "keb_item_id": atom["keb_item_id"],
        "canonical_bundle_digest": EXPECTED_BUNDLE,
        "dow_merge_sha": EXPECTED_DOW_MERGE,
        "authority_transfer": False,
        "formal_credit_delta": 0,
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
