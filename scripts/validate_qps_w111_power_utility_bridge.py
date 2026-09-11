#!/usr/bin/env python3
"""Fail-closed validator for the W111 QPS power/utility KEB bridge.

This validator checks CODEX-owned semantic/provenance invariants only. It does not
fetch confidential bidder files and cannot promote QPS engineering state.
"""
from __future__ import annotations

from pathlib import Path
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "triage" / "W111_QPS_POWER_UTILITY_KEB_BRIDGE.yaml"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    data = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    require(isinstance(data, dict), "manifest must be a mapping")
    require(data.get("repo") == "GBOGEB/CODEX", "CODEX repo identity mismatch")
    require(data.get("authority_scope") == "REPO_LOCAL_SEMANTIC_RUNTIME", "invalid authority scope")
    require(data.get("engineering_promotion_forbidden") is True, "QPS promotion must be forbidden in CODEX")

    child = data.get("qps_child_authority", {})
    require(child.get("repo") == "GBOGEB/cryoplant-project", "child authority repo mismatch")
    require(child.get("source_ssot") == "ocd-adr/20_canonical/control/QPS_W111_POWER_UTILITY_SOURCE_SSOT_v1.json", "wrong W111 source SSOT")
    require(len(str(child.get("source_ssot_git_blob_sha", ""))) == 40, "child source SSOT git blob SHA required")

    taxonomy = data.get("semantic_taxonomy", {})
    require(set(taxonomy.get("electrical_boundary", {})) == {"E0", "E1", "E2", "E3", "E4"}, "E0-E4 boundary incomplete")
    require(set(taxonomy.get("thermal_boundary", {})) == {"T0", "T1", "T2", "T3", "T4", "T5"}, "T0-T5 boundary incomplete")

    inv = set(data.get("hard_invariants", []))
    for marker in (
        "stale_52p4Hz_interpolation_is_rejected",
        "unknown_auxiliary_HVAC_UPS_fan_or_pump_load_is_not_zero",
        "315kW_motor_rating_is_not_357kW_package_input",
        "returned_cold_must_be_accounted_once_across_a_declared_control_volume",
        "derived_MC_PCA_BT_outputs_never_promote_QPS_state",
    ):
        require(marker in inv, f"missing invariant: {marker}")

    known = data.get("canonical_known_values_for_semantic_regression_only", {})
    normal = known.get("LKT_HP_normal", {})
    require(normal.get("frequency_Hz") == 56.0, "immutable LKT HP normal frequency must be 56 Hz")
    require(normal.get("total_flow_g_s") == 326.0, "immutable LKT HP total flow must be 326 g/s")
    require(normal.get("flow_each_g_s") == 81.5, "immutable equal-share flow must be 81.5 g/s")
    require(normal.get("inlet_P_bara") == 1.05 and normal.get("outlet_P_bara") == 14.0, "immutable HP pressure boundary mismatch")

    max_ref = known.get("LKT_HP_max_reference_each", {})
    require(max_ref.get("motor_rating_kW") == 315.0, "FSD575 motor rating regression")
    require(max_ref.get("package_input_kW") == 357.0, "FSD575 package input regression")

    ingress = data.get("ingress_contract", {})
    prohibited = set(ingress.get("prohibited_payload", []))
    require("raw_confidential_bidder_pdf_bytes" in prohibited, "confidential source guard missing")

    print("QPS_W111_KEB_BRIDGE_VALIDATION=PASS")
    print("engineering_promotion_forbidden=true")
    print("boundaries=E0-E4,T0-T5")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print("QPS_W111_KEB_BRIDGE_VALIDATION=FAIL", file=sys.stderr)
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
