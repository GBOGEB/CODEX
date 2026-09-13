#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

SOURCE = Path("docs/qps_m05/QPS_G5_KEB_CHALLENGE_v0.1.json")
OUT = Path("artifacts/m05/g5_keb_challenge_receipt.json")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def main() -> int:
    raw = SOURCE.read_bytes()
    data = json.loads(raw)
    require(data["schema"] == "qps.g5.keb_challenge.v1", "schema mismatch")
    require(data["mission"] == "MISSION_H2_KEB", "mission mismatch")
    require(data["local_mission"] == "M05_PROVENANCE_ATTESTATION", "local mission mismatch")
    require(data["authority"] == "SEMANTIC_PROVENANCE_CHALLENGE_ONLY_NOT_ENGINEERING_ACCEPTANCE", "authority mismatch")

    execution = data["execution"]
    require(execution["repo"] == "GBOGEB/Q_engineering_tools", "executor repo mismatch")
    require(execution["pr"] == 19, "executor PR mismatch")
    require(execution["run"] == 34730906661, "run mismatch")
    require(execution["job"] == 103653394137, "job mismatch")
    require(execution["runner_id"] != 0, "zero-step/preexecution class cannot pass KEB")
    require(execution["exact_child_blobs_proved"] == "3_of_3", "exact blob proof incomplete")
    require(execution["result"] == "PASS_EXECUTED_EXACT_PAYLOAD", "runtime result mismatch")
    require(execution["artifact_digest"].startswith("sha256:"), "artifact digest missing")
    require(len(execution["projection_sha256"]) == 64, "projection digest malformed")

    contract = data["semantic_contract"]
    require(contract["states"] == ["OP", "COLD_SB", "RUNDOWN"], "state identity drift")
    required = {
        "spare_id",
        "spare_cost",
        "spare_lead_time_h",
        "MTTR_h",
        "MDT_h",
        "labour",
        "recovery_energy",
        "helium_consumables",
        "downtime_rate",
    }
    require(set(contract["required_hook_fields"]) == required, "G5 hook vocabulary drift")
    require(contract["unknown_numeric_semantics"] == "NULL_NOT_ZERO", "unknown semantics drift")
    require(contract["actual_numeric_cost_rows_ready"] == "0_of_3", "numeric readiness overstated")
    require(contract["actual_numeric_cost_release"] == "WITHHELD_SOURCE_VALUES", "numeric release must remain withheld")
    require(contract["source_value_gates"] == [974, 981], "source-value gate drift")
    require(set(contract["forbidden_inferences"]) == {
        "ENERGY_TO_SPARES",
        "RELIABILITY_TO_SPARE_PRICE",
        "MISSING_COST_MDT_LEADTIME_IMPUTATION",
    }, "forbidden inference vocabulary drift")
    require(contract["test_vector_authority"] == "NON_ENGINEERING_EXCLUDED", "test-vector authority drift")

    predicate = data["challenge_predicate"]
    require(all(predicate[key] for key in [
        "require_exact_lineage",
        "require_runner_nonzero",
        "require_steps_gt_zero",
        "require_artifact_digest",
        "require_null_preservation",
        "require_no_proxy_inference",
        "require_numeric_release_withheld",
    ]), "challenge predicate weakened")
    require(predicate["promotion_authority"] is False, "KEB cannot self-promote child engineering state")

    receipt = {
        "schema": "qps.g5.keb_challenge_receipt.v1",
        "source_contract_sha256": hashlib.sha256(raw).hexdigest(),
        "runtime_execution": "PASS_EXECUTED_EXACT_PAYLOAD",
        "semantic_lineage": "PASS",
        "vocabulary_governance": "PASS",
        "null_preservation": "PASS",
        "forbidden_inference_guard": "PASS",
        "numeric_cost_release": "WITHHELD_SOURCE_VALUES",
        "source_value_gates": [974, 981],
        "keb_disposition": "ACCEPT_SEMANTIC_PROVENANCE_ONLY",
        "promotion_authority": False,
        "next_required_hop": "MISSION_H3_DOW_INDEPENDENT_CONSUMPTION",
        "status": "PASS",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    digest = hashlib.sha256(OUT.read_bytes()).hexdigest()
    print(json.dumps(receipt, sort_keys=True))
    print(f"G5_KEB_CHALLENGE_RECEIPT_SHA256={digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
