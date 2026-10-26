"""CODE PURPLE N+6 stage-only slow-burn control over canonical Mycelium W34.

No polling, subprocess, GitHub API, CREW launch or merge side effect.
Consumes externally captured W33 observations, never synthesizes N+j pulses.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime
from scripts.id_scheduler_dependency_gate import stage, validate

SCHEMA = "missioncontrol.mycelium.nplus.slowburn.v1"
WAKE = {
    "DEFER_STALE_SOURCE_HEAD": "REFRESH_EXACT_OWNER_HEAD",
    "DEFER_POOL_CAPACITY_UNKNOWN": "REQUIRE_NATIVE_POOL_INVENTORY",
    "DEFER_POOL_FULL": "AWAIT_OBSERVED_RUNNER_RELEASE",
    "DEFER_POOL_RESERVED_BY_OTHER_PROPOSAL": "AWAIT_NEXT_NATIVE_POOL_PULSE",
    "DEFER_CHANGED_PATH_LOCK": "WAIT_CHANGED_PATH_LEASE",
    "DEFER_ALREADY_STAGED": "REQUIRE_DISTINCT_NATIVE_RETURN",
    "DEFER_PULSE_BUDGET": "NEXT_DISTINCT_SOURCE_PULSE",
}

def _instant(value):
    if not isinstance(value, str):
        raise ValueError("SOURCE_OBSERVATION_TIME_MISSING")
    try:
        moment = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("SOURCE_OBSERVATION_TIME_INVALID") from exc
    if moment.tzinfo is None or moment.utcoffset() is None:
        raise ValueError("SOURCE_OBSERVATION_TIME_NAIVE")
    return moment

def plan(history, *, horizon=6, max_proposals=4):
    """Stage at most four *proposals* per genuine supplied observation.

    Later epochs must be supplied by a source collector; no staging is executed.
    Once a task is staged, even a renamed request cannot stage it again without
    an independent native return and a new owner disposition outside this plan.
    """
    if type(horizon) is not int or not 6 <= horizon <= 12:
        raise ValueError("HORIZON_REQUIRES_SIX_TO_TWELVE")
    if type(max_proposals) is not int or not 1 <= max_proposals <= 4:
        raise ValueError("UNBOUNDED_STAGE_PROPOSALS")
    if not isinstance(history, list) or not 1 <= len(history) <= horizon + 1:
        raise ValueError("INVALID_OBSERVATION_HISTORY")
    seen_sources, leased_tasks = set(), set()
    prior_time, repos = None, None
    epochs = []
    total_proposed = 0
    for index, entry in enumerate(history):
        if not isinstance(entry, dict) or not isinstance(entry.get("metrics"), dict):
            raise ValueError("MISSING_W33_EPOCH_METRICS")
        metrics = entry["metrics"]
        reqs = entry.get("requests")
        # Canonical W34 validator also rejects remote mutation, unsafe paths,
        # fabricated pool capacity, invalid reward and duplicate task identity.
        validate(metrics, reqs, max_proposals=max_proposals)
        captured = _instant(metrics.get("capture_utc"))
        if prior_time is not None and captured <= prior_time:
            raise ValueError("REPLAYED_OR_REVERSED_EPOCH_TIME")
        prior_time = captured
        population = frozenset(metrics["sources"])
        if repos is not None and repos != population:
            raise ValueError("SOURCE_POPULATION_DRIFT")
        repos = population
        digest = metrics["source_digest"]
        if digest in seen_sources:
            epochs.append({
                "label": "N" if index == 0 else "N+" + str(index),
                "source_digest": digest, "captured_at": metrics["capture_utc"],
                "status": "WITHHELD_REUSED_SOURCE_DIGEST",
                "proposals": 0, "decisions": [],
                "wake": "REQUIRE_NEW_NATIVE_SOURCE_RECEIPT",
            })
            continue
        seen_sources.add(digest)
        retained, carried = [], []
        for req in reqs:
            lease = (req["repo"], req["task_id"], req["head_sha"])
            if lease in leased_tasks:
                carried.append({
                    "id": req["id"], "task_id": req["task_id"],
                    "decision": "DEFER_ALREADY_STAGED_AWAIT_NATIVE_RETURN",
                    "wake": "REQUIRE_DISTINCT_NATIVE_RETURN",
                    "native_job_launch": None,
                })
            else:
                retained.append(req)
        native = stage(metrics, retained, max_proposals=max_proposals) if retained else None
        decisions = []
        if native is not None:
            ids = {r["id"]: r for r in retained}
            for decision in native["decisions"]:
                copied = dict(decision)
                copied["wake"] = (
                    "REQUIRE_OWNER_AUTHORIZED_NATIVE_GATE" if copied["decision"] == "STAGED_NOT_DISPATCHED"
                    else WAKE.get(copied["decision"], "REFRESH_DEPENDENCY_EVIDENCE"))
                decisions.append(copied)
                if copied["decision"] == "STAGED_NOT_DISPATCHED":
                    req = ids[copied["id"]]
                    leased_tasks.add((req["repo"], req["task_id"], req["head_sha"]))
        decisions.extend(carried)
        proposals = native["staged_proposals"] if native else 0
        total_proposed += proposals
        epochs.append({
            "label": "N" if index == 0 else "N+" + str(index),
            "source_digest": digest, "captured_at": metrics["capture_utc"],
            "status": "ADVISORY_STAGE_ONLY",
            "proposals": proposals,
            "decisions": sorted(decisions, key=lambda row: row["id"]),
            "wake": "REQUIRE_NEW_NATIVE_SOURCE_RECEIPT",
        })
    unique = len(seen_sources)
    report = {
        "schema": SCHEMA, "requested_horizon": horizon,
        "required_genuine_source_observations": horizon + 1,
        "observations_supplied": len(history),
        "distinct_source_digests": unique,
        "status": ("STAGE_ONLY_NPLUS_CANDIDATE" if unique >= horizon + 1
                   else "WITHHELD_INCOMPLETE_NPLUS_HISTORY"),
        "epochs": epochs, "stage_only_proposals": total_proposed,
        "native_worker_launches": 0, "cross_repo_mutations": 0,
        "operational_coverage_improvement": None,
        "semantic_root_closure": None,
        "source_receipt_authentication": "EXTERNAL_OWNER_VERIFICATION_REQUIRED",
        "evidence_class": "READ_ONLY_PROPOSED_NOT_EXECUTED",
        "next_trigger": "DISTINCT_TIMESTAMPED_W33_NATIVE_RECEIPT",
        "merge_admission": "HOLD", "authority_transfer": False,
        "formal_credit_delta": 0,
        "mip": {"modernize": "reuse W33/W34 canonical owners",
                "innovate": "bounded six-wave leases and stop reasons",
                "perpetuate": "dedup and evidence-triggered restarts"},
        "dmaic": {"define": "disjoint bounded stage-only work",
                  "measure": "distinct source receipts not fabricated time ticks",
                  "analyze": "blocked and deferred root pressure separate from queues",
                  "improve": "no re-stage of unresolved logical task",
                  "control": "owner-local authorization remains mandatory"},
    }
    report["plan_sha256"] = hashlib.sha256(json.dumps(
        {k: v for k, v in report.items() if k != "plan_sha256"},
        sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return report
