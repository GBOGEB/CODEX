#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

SOURCE = Path("docs/qps_m05/QPS_G5_KEB_CHALLENGE_v0.2.json")
OUT = Path("artifacts/m05/g5_keb_challenge_receipt.json")

EXPECTED_SOURCE = {
    "child_repo": "GBOGEB/cryoplant-project",
    "child_pr": 1043,
    "child_candidate_head": "8fe7c704620336087152a952101e12f7002d47a8",
    "child_merge": "4484f934c705c051563efd3d9c0a6cef39a8d93a",
    "ledger_blob": "525b34004838e9131f26d4d6068390274df0063c",
    "bridge_blob": "7b9a0f3b72eefbeaafd1dba05a20e4cfe4cf2a95",
    "generator_blob": "2574354f7883a6b92a4241a060bf846c3b9c5174",
}

EXPECTED_PAYLOAD_STEPS = [
    {
        "number": 3,
        "name": "Prove exact child payload blobs",
        "status": "completed",
        "conclusion": "success",
    },
    {
        "number": 4,
        "name": "Execute exact G5 COST RCM spares hook generator",
        "status": "completed",
        "conclusion": "success",
    },
    {
        "number": 5,
        "name": "Bind federated execution provenance",
        "status": "completed",
        "conclusion": "success",
    },
]

EXPECTED_EXECUTION = {
    "repo": "GBOGEB/Q_engineering_tools",
    "pr": 19,
    "executor_merge": "16179ddb8c36e8b19cf057ce22d9489f54ca6d13",
    "head": "3a42c50bde4c8827cfc5cc6c11648827301c4f54",
    "run": 34730906661,
    "job": 103653394137,
    "job_name": "g5-exact",
    "job_conclusion": "success",
    "runner_id": 1000260663,
    "observed_completed_step_count": 8,
    "required_payload_steps": EXPECTED_PAYLOAD_STEPS,
    "artifact_id": 10309790070,
    "artifact_name": "qps-reliability-g5-federated-receipt",
    "artifact_size_bytes": 2650,
    "artifact_digest": (
        "sha256:9b71d43c2bafd913e9780174a92514e72511bb8a31fec2cfa065745b58effb9a"
    ),
    "projection_sha256": (
        "97be102020859048940cbe255224c36bb786ff19b31ea7483af2c9f898b4e450"
    ),
    "exact_child_blobs_proved": "3_of_3",
    "result": "PASS_EXECUTED_EXACT_PAYLOAD",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def require_exact(actual: object, expected: object, label: str) -> None:
    require(actual == expected, f"{label} mismatch")


def main() -> int:
    raw = SOURCE.read_bytes()
    data = json.loads(raw)

    require_exact(data["schema"], "qps.g5.keb_challenge.v2", "schema")
    require_exact(
        data["supersession_reason"],
        "POST_MERGE_REPAIR_CODEX_671_P1_P2",
        "supersession reason",
    )
    require_exact(data["mission"], "MISSION_H2_KEB", "mission")
    require_exact(
        data["local_mission"],
        "M05_PROVENANCE_ATTESTATION",
        "local mission",
    )
    require_exact(
        data["authority"],
        "SEMANTIC_PROVENANCE_CHALLENGE_ONLY_NOT_ENGINEERING_ACCEPTANCE",
        "authority",
    )

    require_exact(data["source"], EXPECTED_SOURCE, "exact source lineage")
    execution = data["execution"]
    require_exact(execution, EXPECTED_EXECUTION, "exact execution lineage")
    require(execution["runner_id"] > 0, "runner assignment must be nonzero")
    require(
        execution["observed_completed_step_count"] > 0,
        "observed completed step count must be >0",
    )
    require(
        len(execution["required_payload_steps"]) > 0,
        "required payload step list must be nonempty",
    )
    for step in execution["required_payload_steps"]:
        require_exact(step["status"], "completed", "payload step status")
        require_exact(step["conclusion"], "success", "payload step conclusion")
    require(
        execution["observed_completed_step_count"]
        >= len(execution["required_payload_steps"]),
        "completed step count cannot be smaller than required payload steps",
    )

    contract = data["semantic_contract"]
    require_exact(contract["states"], ["OP", "COLD_SB", "RUNDOWN"], "states")
    required_fields = {
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
    require_exact(
        set(contract["required_hook_fields"]),
        required_fields,
        "G5 hook vocabulary",
    )
    require_exact(
        contract["unknown_numeric_semantics"],
        "NULL_NOT_ZERO",
        "unknown semantics",
    )
    require_exact(
        contract["actual_numeric_cost_rows_ready"],
        "0_of_3",
        "numeric readiness",
    )
    require_exact(
        contract["actual_numeric_cost_release"],
        "WITHHELD_SOURCE_VALUES",
        "numeric release",
    )
    require_exact(contract["source_value_gates"], [974, 981], "source gates")
    require_exact(
        set(contract["forbidden_inferences"]),
        {
            "ENERGY_TO_SPARES",
            "RELIABILITY_TO_SPARE_PRICE",
            "MISSING_COST_MDT_LEADTIME_IMPUTATION",
        },
        "forbidden inference vocabulary",
    )
    require_exact(
        contract["test_vector_authority"],
        "NON_ENGINEERING_EXCLUDED",
        "test-vector authority",
    )

    predicate = data["challenge_predicate"]
    required_predicates = [
        "require_exact_lineage",
        "require_exact_artifact_identity",
        "require_exact_digest_values",
        "require_runner_nonzero",
        "require_observed_completed_steps_gt_zero",
        "require_required_payload_steps_completed",
        "require_null_preservation",
        "require_no_proxy_inference",
        "require_numeric_release_withheld",
    ]
    require(
        all(predicate[key] is True for key in required_predicates),
        "challenge predicate weakened",
    )
    require(
        predicate["promotion_authority"] is False,
        "KEB cannot self-promote child engineering state",
    )

    receipt = {
        "schema": "qps.g5.keb_challenge_receipt.v2",
        "source_contract_sha256": hashlib.sha256(raw).hexdigest(),
        "source_lineage_sha256": hashlib.sha256(
            json.dumps(EXPECTED_SOURCE, sort_keys=True).encode("utf-8")
        ).hexdigest(),
        "execution_lineage_sha256": hashlib.sha256(
            json.dumps(EXPECTED_EXECUTION, sort_keys=True).encode("utf-8")
        ).hexdigest(),
        "runtime_execution": "PASS_EXECUTED_EXACT_PAYLOAD",
        "observed_completed_step_count": execution["observed_completed_step_count"],
        "required_payload_steps_completed": len(EXPECTED_PAYLOAD_STEPS),
        "semantic_lineage": "PASS_EXACT_EXPECTED_IDENTITIES",
        "artifact_identity": "PASS_EXACT_ID_NAME_SIZE_DIGEST",
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
    OUT.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    digest = hashlib.sha256(OUT.read_bytes()).hexdigest()
    print(json.dumps(receipt, sort_keys=True))
    print(f"G5_KEB_CHALLENGE_RECEIPT_SHA256={digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
