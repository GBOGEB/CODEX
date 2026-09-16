#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ATOM = ROOT / "ssot" / "bridge_rows" / "gg_math_temporal_pca_w4_p31_knowledge_atom.json"
SOURCE_RECEIPT = ROOT / "ssot" / "bridge_rows" / "gg_math_temporal_pca_w4_p31.yaml"

REQUIRED = {
    "keb_item_id",
    "object_type",
    "source_repo",
    "source_pr",
    "source_sha",
    "source_locator",
    "source_digest",
    "replay_status",
    "validation_result",
    "downstream_consumer",
    "next_action",
    "lineage",
}
EXPECTED_CLOCKS = ["k", "t", "a", "wave", "pulse", "pr", "run", "release"]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-sha", required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    atom = json.loads(ATOM.read_text(encoding="utf-8"))
    missing = sorted(REQUIRED - set(atom))
    require(not missing, f"missing required fields {missing}")
    require(re.fullmatch(r"KEB-ITEM-[0-9]{4}", atom["keb_item_id"]) is not None, "invalid keb_item_id")
    require(atom["keb_item_id"] == "KEB-ITEM-0002", "unexpected atom id")
    require(atom["object_type"] == "KEB_KNOWLEDGE_ATOM", "not a knowledge atom")
    require(atom["source_repo"] == "GBOGEB/gg_MATH", "source repo drift")
    require(atom["source_pr"] == 15, "source PR drift")
    require(atom["source_sha"] == "a99d7cacd03ed3a392c063a1b3f8dbffdba0d060", "source SHA drift")
    require(atom["source_locator"] == "https://github.com/GBOGEB/gg_MATH/actions/runs/35138067439", "source locator drift")
    require(atom["source_digest"] == "sha256:876c55c759de33392985f693f1735cdc0d38dda7d7b7a6c80ee80aee33fd8405", "source digest drift")
    require(atom["replay_status"] == "PASS", "replay status not PASS")
    require(atom["validation_result"] == "PASS_INDEPENDENT_DOW_EXACT_LIVE_A3_SYNTHETIC_ONLY", "validation result drift")
    require(atom["downstream_consumer"] == "GBOGEB/cryoplant-project/QPS_TRIAGE", "downstream consumer drift")

    lineage = atom["lineage"]
    require(all(lineage.get(k) for k in ("chat_session", "originating_prompt", "created_by")), "lineage incomplete")

    provider = atom["provider_runtime"]
    require(provider["artifact_digest"] == atom["source_digest"], "provider/source digest mismatch")
    require(provider["exact_head_sha"] == atom["source_sha"], "provider/source SHA mismatch")
    require(provider["workflow_run_id"] == 35138067439, "provider run drift")
    require(provider["artifact_id"] == 10463852915, "provider artifact drift")
    require(provider["result"] == "PASS", "provider result drift")
    require(len(provider["challenges"]) == 7 and len(set(provider["challenges"])) == 7, "C01-C07 coverage drift")

    fed = atom["grandmission_i_b_federation"]
    require(fed["exact_head_sha"] == "a5f32ef2b65caa9b49270d7fe8134acd6f1e71d8", "federation head drift")
    require(fed["merge_sha"] == "e9afd4131bde2071d184d0e3c5326b82f5756faa", "federation merge drift")
    require(fed["workflow_run_id"] == 35139956561, "federation run drift")
    require(fed["artifact_digest"] == "sha256:2c7cbcddffc6c3830ab02a212563ef390e7fe189ce24214f4313e6e5bccd2921", "federation artifact digest drift")
    require(fed["federation_receipt_digest"] == "sha256:84a2869fca566eb14879e85b5777af8027c6aa096c3bcc746f8eb838b69ac053", "federation receipt digest drift")
    require(fed["result"] == "PASS", "federation result drift")

    dow = atom["independent_dow_validation"]
    require(dow["repo"] == "GBOGEB/ABACUS" and dow["pr"] == 1252, "DOW identity drift")
    require(dow["exact_head_sha"] == "ff7f3b4b5c8c830a2b956c7f04462a9341559f35", "DOW exact head drift")
    require(dow["merge_sha"] == "835c6f36c93c736336b5f87d5963d43e37bf3684", "DOW merge drift")
    require(dow["workflow_run_id"] == 35145377318, "DOW run drift")
    require(dow["workflow_job_id"] == 104959918522, "DOW job drift")
    require(dow["artifact_id"] == 10466506978, "DOW artifact id drift")
    require(dow["artifact_digest"] == "sha256:3598d5b46baf614d0cef6f318b2fbb3160913c32d84920e0edf5a36f960d2cf9", "DOW artifact digest drift")
    require(dow["result"] == "PASS_EXACT_HEAD_FAIL_CLOSED_LINEAGE_VALIDATION", "DOW result drift")
    require(dow["unrelated_broad_suite_reds_compensated"] is False, "unrelated red compensation forbidden")

    claims = atom["knowledge_claims"]
    require(claims["named_clocks_preserved"] == EXPECTED_CLOCKS, "named clock roundtrip drift")
    require(claims["raw_pca_loading_sign_is_not_physical_direction"] is True, "PCA sign doctrine drift")
    require(claims["attenuation_toward_parity_is_distinct_from_direction_reversal"] is True, "attenuation doctrine drift")

    guards = atom["authority_guards"]
    require(guards["authority_transfer"] is False, "authority transfer forbidden")
    require(guards["hard_gate_compensation_allowed"] is False, "hard gate compensation forbidden")
    require(guards["formal_engineering_credit_delta"] == 0, "formal credit must remain zero")
    require(guards["negotiation_credit_delta"] == 0, "negotiation credit must remain zero")
    require(guards["engineering_acceptance_created"] is False, "engineering acceptance forbidden")
    require(guards["runtime_gold_created"] is False, "runtime GOLD forbidden")

    interpretations = atom["interpretation_guards"]
    require(all(v is False for v in interpretations.values()), "interpretation guard inversion")

    source_receipt_text = SOURCE_RECEIPT.read_text(encoding="utf-8")
    require("object_type: KEB_SOURCE_RECEIPT" in source_receipt_text, "source receipt type changed")
    require("state: ACCEPT_PROVIDER_BOUND_READY_DOW_CYCLE2" in source_receipt_text, "source receipt not provider-bound")
    require("source_sha: a5f32ef2b65caa9b49270d7fe8134acd6f1e71d8" in source_receipt_text, "source receipt federation head drift")

    atom_digest = "sha256:" + hashlib.sha256(ATOM.read_bytes()).hexdigest()
    receipt = {
        "schema": "codex.keb.gg_math_temporal_pca_knowledge_atom_validation.v1",
        "source_control_sha": args.source_sha,
        "keb_item_id": atom["keb_item_id"],
        "object_type": atom["object_type"],
        "provider_source_sha": atom["source_sha"],
        "provider_source_digest": atom["source_digest"],
        "atom_file_digest": atom_digest,
        "dow_validation_run_id": dow["workflow_run_id"],
        "dow_validation_artifact_digest": dow["artifact_digest"],
        "result": "PASS_REAL_KEB_KNOWLEDGE_ATOM",
        "authority_transfer": False,
        "formal_credit_delta": 0,
        "hard_gate_compensation_allowed": False,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(receipt["result"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
