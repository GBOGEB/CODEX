#!/usr/bin/env python3
"""CODEX/KEB independent P4 semantic candidate for gg_MATH -> QPS.

Contract-only observer. Matching a hash does not authenticate provider runtime
or authorize QPS project thresholds, decisions, or downstream promotion.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path, PurePosixPath
from typing import Any

SHA = re.compile(r"^[0-9a-f]{40}$")
DIGEST = re.compile(r"^[0-9a-f]{64}$")
ROUTE = ["GBOGEB/gg_MATH", "GBOGEB/CODEX", "GBOGEB/ABACUS", "GBOGEB/cryoplant-project"]
METHODS = {"M03_COVARIANCE", "M04_PCA", "M05_CONFIDENCE_INTERVALS", "M08_BRADLEY_TERRY", "M12_TEMPORAL_STATE"}
FIELDS = {"schema", "route_id", "route", "producer", "method", "lineage",
          "execution", "authority", "completed_hops", "receipt_sha256"}
AUTH = {"authority_transfer": False, "formal_credit_delta": 0,
        "engineering_acceptance": False, "hard_gate_compensation_allowed": False,
        "release_credit": False}
EXEC = {"state": "PROPOSED_UNVERIFIED", "run_id": None,
        "job_id": None, "positive_steps": None}


def digest(value: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(value, separators=(",", ":"), sort_keys=True,
        allow_nan=False, ensure_ascii=True).encode("utf-8")).hexdigest()


def challenge(item: Any, *, source_sha: str, artifact_sha256: str) -> dict[str, Any]:
    errors = []
    if not isinstance(item, dict) or set(item) != FIELDS:
        errors.append("ENVELOPE_SCHEMA_OR_PRIVATE_FIELDS")
    else:
        body = {k: v for k, v in item.items() if k != "receipt_sha256"}
        try:
            if digest(body) != item["receipt_sha256"]:
                errors.append("CANONICAL_DIGEST_MISMATCH")
        except (ValueError, TypeError, OverflowError):
            errors.append("NONCANONICAL_ENVELOPE")
        if item["schema"] != "gg-math-qps-wormhole/v1" or item["route_id"] != "QPS-MATH-P4-3P3-V1":
            errors.append("CONTRACT_OR_ROUTE_VERSION_MISMATCH")
        if item["route"] != ROUTE or item["completed_hops"] != []:
            errors.append("UNVERIFIED_HOP_OR_ROUTE_MUTATION")
        p = item["producer"]
        if not isinstance(p, dict) or set(p) != {"repo", "source_sha", "artifact_path", "artifact_sha256"}:
            errors.append("PRODUCER_IDENTITY_INVALID")
        else:
            path = p.get("artifact_path")
            safe = isinstance(path, str) and bool(path) and ":" not in path and "\\" not in path and not PurePosixPath(path).is_absolute() and all(v not in (".", "..") for v in path.split("/"))
            if p["repo"] != ROUTE[0] or p["source_sha"] != source_sha or not isinstance(source_sha, str) or not SHA.fullmatch(source_sha):
                errors.append("EXACT_SOURCE_IDENTITY_MISMATCH")
            if p["artifact_sha256"] != artifact_sha256 or not isinstance(artifact_sha256, str) or not DIGEST.fullmatch(artifact_sha256) or not safe:
                errors.append("EXACT_ARTIFACT_IDENTITY_MISMATCH")
        m = item["method"]
        if not isinstance(m, dict) or set(m) != {"id", "population_id", "data_class", "threshold_authority", "observed_pairwise_fitted"}:
            errors.append("MATH_METHOD_SHAPE_INVALID")
        else:
            ident = m["id"]
            pop = m["population_id"]
            if not isinstance(ident, str) or ident not in METHODS:
                errors.append("UNKNOWN_MATH_METHOD")
            if m["threshold_authority"] != "QPS_ONLY" or m["observed_pairwise_fitted"] is not False:
                errors.append("QPS_THRESHOLD_OR_BT_AUTHORITY_INVERSION")
            if m["data_class"] != "SYNTHETIC_REFERENCE" or not isinstance(pop, str) or not pop.startswith("SYNTHETIC_") or not pop.isascii():
                errors.append("OBSERVED_DATA_CLAIM_NOT_SUPPORTED")
        if item["authority"] != AUTH or item["execution"] != EXEC:
            errors.append("FAKE_AUTHORITY_OR_EXECUTION")
        l = item["lineage"]
        if not isinstance(l, dict) or set(l) != {"wave", "pulse", "qps_child_state"} or l.get("qps_child_state") != "UNKNOWN" or not all(isinstance(l.get(k), str) and l[k] for k in ("wave", "pulse")):
            errors.append("QPS_CHILD_DECISION_INJECTION")
    body = {
        "schema": "codex.keb.qps_math_wormhole_candidate/v1",
        "semantic_owner": "CODEX/KEB",
        "provider_sha": source_sha,
        "artifact_sha256": artifact_sha256,
        "status": "SEMANTIC_CANDIDATE_ONLY" if not errors else "DEFER_INVALID_SEMANTICS",
        "errors": sorted(set(errors)),
        "native_provider_run_authenticated": False,
        "keb_native_run_authenticated": False,
        "eligible_for_dow_authenticated_replay": False,
        "qps_child_disposition": "DEFER",
        "knowledge_only": True,
        "authority_transfer": False,
        "formal_credit_delta": 0,
        "engineering_acceptance": False,
    }
    return {**body, "receipt_sha256": digest(body)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--provider-receipt", type=Path, required=True)
    ap.add_argument("--provider-sha", required=True)
    ap.add_argument("--artifact-sha256", required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    raw = args.provider_receipt.read_bytes()
    if len(raw) > 1_048_576:
        raise ValueError("provider receipt too large")
    out = challenge(json.loads(raw), source_sha=args.provider_sha, artifact_sha256=args.artifact_sha256)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": out["status"], "errors": out["errors"]}, sort_keys=True))
    return 0 if out["status"] == "SEMANTIC_CANDIDATE_ONLY" else 1


if __name__ == "__main__":
    raise SystemExit(main())
