#!/usr/bin/env python3
"""CODE PURPLE OVERTIME planner: filtered, read-only work-conserving selection.

This plans independent safe microtasks for observed spare runner windows.
It never launches workers, touches a remote repo, mutates branch protection,
approves review/security gates or grants engineering authority.
"""
from __future__ import annotations

import argparse
import json
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from scripts.id_work_conserving_scheduler import Item, choose

SHA = re.compile(r"^[0-9a-f]{40}$")
SAFE_KINDS = {"READ_ONLY_SCOUT", "LINK_AUDIT", "RECEIPT_QA", "VISUAL_SOURCE_QA", "DETERMINISTIC_DOC_PREVIEW"}
FORBIDDEN_TAGS = {"SECURITY_APPROVAL", "OWNER_ATTESTATION", "RULESET_CHANGE", "ENGINEERING_ACCEPTANCE", "CROSS_REPO_MUTATION"}
MAX_CANDIDATES = 256


@dataclass(frozen=True)
class Rejection:
    id: str
    reason: str


def plan(snapshot: dict[str, Any]) -> dict[str, Any]:
    """Return a plan, not dispatch evidence; fail closed on absent capacity."""
    if snapshot.get("schema") != "code-purple.overtime.input/0.1":
        raise ValueError("unsupported queue schema")
    observed = snapshot.get("capacity")
    tasks = snapshot.get("tasks")
    if not isinstance(observed, dict) or not isinstance(tasks, list) or len(tasks) > MAX_CANDIDATES:
        raise ValueError("capacity and bounded tasks are required")
    workers = observed.get("free_workers")
    receipt = observed.get("capacity_proof_ref")
    if not isinstance(workers, list) or not isinstance(receipt, str) or not receipt:
        return {
            "status": "HOLD_NO_MEASURED_CAPACITY",
            "dispatch_plan_only": [],
            "count_eligible": 0, "count_rejected": len(tasks),
            "reasons": ["capacity proof and free worker list absent"],
            "execution_claim": "NOT_DISPATCHED",
        }
    if not isinstance(observed.get("critical_lane_resume_s"), (int, float)):
        raise ValueError("critical_lane_resume_s is required for a bounded idle window")
    window = float(observed["critical_lane_resume_s"])
    if not 0 < window <= 3600:
        raise ValueError("bounded overtime window must be in (0, 3600] seconds")
    if len(workers) > 128:
        raise ValueError("too many worker descriptors")
    seen_tasks: set[str] = set()
    candidates: list[tuple[dict[str, Any], Item]] = []
    rejected: list[Rejection] = []
    for raw in tasks:
        if not isinstance(raw, dict) or not isinstance(raw.get("id"), str):
            raise ValueError("task must have string id")
        tid = raw["id"]
        if tid in seen_tasks:
            raise ValueError("duplicate task identifier")
        seen_tasks.add(tid)
        if raw.get("state") != "QUEUED":
            rejected.append(Rejection(tid, "NOT_QUEUED"))
            continue
        tags = raw.get("tags", [])
        if not isinstance(tags, list) or not all(isinstance(x, str) for x in tags):
            rejected.append(Rejection(tid, "INVALID_TAGS"))
            continue
        if raw.get("kind") not in SAFE_KINDS or FORBIDDEN_TAGS.intersection(tags):
            rejected.append(Rejection(tid, "NOT_LOW_RISK_INDEPENDENT"))
            continue
        if raw.get("read_only") is not True or raw.get("dependencies_complete") is not True:
            rejected.append(Rejection(tid, "MUTATION_OR_UNMET_DEPENDENCY"))
            continue
        if raw.get("checkpoint_resumable") is not True or raw.get("shared_write_lock") is not False:
            rejected.append(Rejection(tid, "UNSAFE_PREEMPTION_OR_OVERLAP"))
            continue
        if raw.get("human_approval_required") is not False or raw.get("sensitive_inputs") is not False:
            rejected.append(Rejection(tid, "OWNER_OR_SENSITIVE_BOUNDARY"))
            continue
        if not (isinstance(raw.get("source_sha"), str) and SHA.fullmatch(raw["source_sha"])):
            rejected.append(Rejection(tid, "UNBOUND_SOURCE_SHA"))
            continue
        if not isinstance(raw.get("receipt_target"), str) or not raw["receipt_target"]:
            rejected.append(Rejection(tid, "MISSING_DURABLE_RECEIPT_TARGET"))
            continue
        required = raw.get("required_skills")
        if not isinstance(required, list) or not all(isinstance(x, str) for x in required):
            rejected.append(Rejection(tid, "INVALID_SKILL_REQUIREMENT"))
            continue
        seconds = raw.get("estimated_seconds")
        if type(seconds) not in (float, int) or not 0 < float(seconds) <= window:
            rejected.append(Rejection(tid, "WONT_FIT_MEASURED_WINDOW"))
            continue
        score_keys = ("convergence_gain", "stability_gain", "unblock_gain", "age_s", "checkpoint_cost_s", "max_queue_s")
        if any(type(raw.get(k, 0)) not in (int, float) or not math.isfinite(float(raw.get(k, 0))) or raw.get(k, 0) < 0 for k in score_keys):
            rejected.append(Rejection(tid, "INVALID_GAIN_OR_AGE"))
            continue
        candidates.append((raw, Item(
            id=tid,
            state="QUEUED",
            est_remaining_s=float(seconds),
            convergence_gain=float(raw.get("convergence_gain", 1)),
            stability_gain=float(raw.get("stability_gain", 0)),
            unblock_gain=float(raw.get("unblock_gain", 0)),
            age_s=float(raw.get("age_s", 0)),
            max_queue_s=float(raw.get("max_queue_s", 300)),
            resumable=True,
            setup_affinity=str(raw.get("kind")),
            checkpoint_cost_s=float(raw.get("checkpoint_cost_s", 0)),
        )))
    # Ranking is delegated to the established CODEX scheduler; no new priority authority.
    ranked = choose([item for _, item in candidates], len(candidates))
    raw_by_id = {raw["id"]: raw for raw, _ in candidates}
    assigned: list[dict[str, Any]] = []
    used_tasks: set[str] = set()
    seen_workers: set[str] = set()
    for worker in workers:
        if not isinstance(worker, dict) or not isinstance(worker.get("id"), str):
            raise ValueError("worker identifiers required")
        if worker["id"] in seen_workers:
            raise ValueError("duplicate worker would imply double capacity")
        seen_workers.add(worker["id"])
        if worker.get("free") is not True or worker.get("observed") is not True:
            continue
        skills = worker.get("skills")
        if not isinstance(skills, list) or not all(isinstance(x, str) for x in skills):
            raise ValueError("worker skills must be listed")
        for candidate in ranked:
            row = raw_by_id[candidate.id]
            if candidate.id in used_tasks:
                continue
            if not set(row["required_skills"]).issubset(set(skills)):
                continue
            assigned.append({
                "worker": worker["id"],
                "task": candidate.id,
                "kind": row["kind"],
                "source_sha": row["source_sha"],
                "receipt_target": row["receipt_target"],
                "estimated_seconds": row["estimated_seconds"],
                "selection": "ADVISORY_ONLY",
            })
            used_tasks.add(candidate.id)
            break
    return {
        "schema": "code-purple.overtime.plan/0.1",
        "status": "PLAN_READY_NOT_DISPATCHED" if assigned else "HOLD_NO_COMPATIBLE_FREE_WORKER",
        "source_capacity_receipt": receipt,
        "window_seconds": window,
        "dispatch_plan_only": assigned,
        "eligible_tasks": len(candidates),
        "rejected_tasks": [r.__dict__ for r in rejected],
        "blocked_by_skill_or_capacity": [p.id for p in ranked if p.id not in used_tasks],
        "execution_claim": "NOT_DISPATCHED",
        "merge_authority": "NONE",
        "security_exception": False,
        "engineering_credit_delta": 0,
        "authority_transfer": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=False)
    args = parser.parse_args()
    result = plan(json.loads(args.input.read_text(encoding="utf-8")))
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
