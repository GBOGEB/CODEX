#!/usr/bin/env python3
"""Fail-closed, read-only reconciliation for a bounded three-pulse G3A mission.

Actual GitHub work is performed by an independently authorised host/connector.
This module does not dispatch commands, authenticate GitHub or grant admission.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

PLAN_SCHEMA = "code-purple.g3a.request.v1"
PULSE_SCHEMA = "code-purple.g3a.pulse.v1"
REPORT_SCHEMA = "code-purple.g3a.reconciliation.v1"
SHA = re.compile(r"^[0-9a-f]{40}$")
DIGEST = re.compile(r"^[0-9a-f]{64}$")
ACTIONS = frozenset(
    {
        "inspect",
        "analyze",
        "measure",
        "test",
        "edit_owned",
        "commit_owned",
        "open_draft_pr",
        "collect_receipt",
    }
)
MANDATORY_STOPS = frozenset(
    {
        "HEAD_DRIFT",
        "POLICY_DRIFT",
        "P0_P1_SECURITY",
        "AUTHORITY_GAP",
        "OWNERSHIP_COLLISION",
        "MISSING_PROOF",
        "BUDGET_EXHAUSTED",
    }
)
RESULTS = frozenset({"MEASURED", "HOLD", "FAIL", "BLOCKED"})
CHECK_RESULTS = frozenset({"PASS", "FAIL", "HOLD", "NOT_RUN"})


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a nonempty string")
    return value


def _hex(value: Any, field: str, pattern: re.Pattern[str]) -> str:
    if not isinstance(value, str) or not pattern.fullmatch(value):
        raise ValueError(f"{field} must be canonical lowercase hex")
    return value


def _paths_collide(a: str, b: str) -> bool:
    a, b = a.rstrip("/"), b.rstrip("/")
    return a == b or a.startswith(b + "/") or b.startswith(a + "/")


def validate_plan(plan: Any) -> dict[str, Any]:
    """Reject unauthorized, unbounded, non-traceable or colliding plans."""
    if not isinstance(plan, dict) or plan.get("schema") != PLAN_SCHEMA:
        raise ValueError("invalid G3A plan schema")
    if plan.get("mode") != "G3A" or plan.get("step_budget") != 3:
        raise ValueError("G3A requires exactly three planned pulses")
    for field in ("mission_id", "repository", "wave_id", "objective"):
        _require_string(plan.get(field), field)
    _hex(plan.get("source_sha"), "source_sha", SHA)
    _hex(plan.get("policy_sha256"), "policy_sha256", DIGEST)
    if plan.get("execution_mode") != "sequential_pulses":
        raise ValueError("pulses must be sequential")
    allowed = plan.get("allowed_actions")
    if (not isinstance(allowed, list) or not allowed or
            any(not isinstance(action, str) or action not in ACTIONS
                for action in allowed) or
            len(allowed) != len(set(allowed))):
        raise ValueError("unauthorized or duplicated actions")
    stops = plan.get("stop_on")
    if (not isinstance(stops, list) or
            any(not isinstance(item, str) for item in stops)):
        raise ValueError("invalid stop conditions")
    if not MANDATORY_STOPS <= set(stops):
        raise ValueError("missing mandatory stop conditions")
    if len(stops) != len(set(stops)):
        raise ValueError("duplicate stop condition")
    steps = plan.get("steps")
    if not isinstance(steps, list) or len(steps) != 3:
        raise ValueError("G3A requires three step intents")
    if [step.get("pulse_id") if isinstance(step, dict) else None
            for step in steps] != ["P1", "P2", "P3"]:
        raise ValueError("step IDs must be P1, P2, P3 in order")
    for step in steps:
        _require_string(step.get("intent"), "step intent")
    scouts, max_writers = plan.get("max_read_scouts"), plan.get("max_write_workers")
    if (type(scouts) is not int or not 0 <= scouts <= 4 or
            type(max_writers) is not int or not 0 <= max_writers <= 2):
        raise ValueError("invalid concurrency budget")
    workers = plan.get("parallel_slices", [])
    if not isinstance(workers, list) or len(workers) > max_writers:
        raise ValueError("parallel slices exceed write budget")
    owners: set[str] = set()
    scope: list[tuple[str, str]] = []
    for worker in workers:
        if not isinstance(worker, dict):
            raise ValueError("invalid slice")
        owner = _require_string(worker.get("owner"), "slice owner")
        if owner in owners:
            raise ValueError("duplicate slice owner")
        owners.add(owner)
        paths = worker.get("write_paths")
        if not isinstance(paths, list) or not paths:
            raise ValueError("missing slice paths")
        for path in paths:
            normal = path.rstrip("/") if isinstance(path, str) else ""
            if (not normal or path.startswith("/") or "\\" in path
                    or "//" in path or
                    any(part in ("", ".", "..") for part in normal.split("/"))):
                raise ValueError("unsafe slice path")
            for prior_owner, prior_path in scope:
                if _paths_collide(path, prior_path):
                    raise ValueError(
                        f"write scope collision: {owner} / {prior_owner}"
                    )
            scope.append((owner, path))
    return plan


def _check_receipt(receipt: Any, plan: dict[str, Any],
                   pulse_id: str) -> dict[str, Any]:
    if not isinstance(receipt, dict) or receipt.get("schema") != PULSE_SCHEMA:
        raise ValueError("invalid pulse receipt schema")
    if (receipt.get("mission_id") != plan["mission_id"] or
            receipt.get("pulse_id") != pulse_id):
        raise ValueError("foreign mission or pulse receipt")
    _hex(receipt.get("input_sha"), "input_sha", SHA)
    _hex(receipt.get("output_sha"), "output_sha", SHA)
    _hex(receipt.get("policy_sha256"), "receipt policy", DIGEST)
    if receipt.get("result") not in RESULTS:
        raise ValueError("invalid pulse result")
    actions = receipt.get("actions")
    if (not isinstance(actions, list) or
            any(action not in plan["allowed_actions"] for action in actions)):
        raise ValueError("pulse requested unauthorized action")
    if receipt.get("independent_admission") is not False:
        raise ValueError("G3A reconciliation cannot assert independent admission")
    checks = receipt.get("checks")
    if not isinstance(checks, list):
        raise ValueError("missing check inventory")
    for check in checks:
        if not isinstance(check, dict) or check.get("status") not in CHECK_RESULTS:
            raise ValueError("invalid check state")
        _require_string(check.get("name"), "check name")
        if check["status"] in {"PASS", "FAIL"}:
            _require_string(check.get("evidence_ref"), "check evidence_ref")
    if receipt["result"] == "MEASURED" and (
        not checks or any(c.get("status") != "PASS" for c in checks)
    ):
        # A PASS alongside a FAIL/HOLD/NOT_RUN must not promote the pulse.
        raise ValueError("MEASURED requires all checks PASS with evidence")
    return receipt


def reconcile(plan: dict[str, Any], receipts: Any) -> dict[str, Any]:
    """Assess up to three sequential pulse receipts without conferring authority."""
    validate_plan(plan)
    if not isinstance(receipts, list) or len(receipts) > 3:
        raise ValueError("receipts must be an array of at most three")
    expected_sha = plan["source_sha"]
    seen: set[str] = set()
    rows: list[dict[str, Any]] = []
    stop_reason: str | None = None
    evidence_count = 0
    for index, item in enumerate(receipts):
        pulse_id = f"P{index + 1}"
        receipt = _check_receipt(item, plan, pulse_id)
        if pulse_id in seen:
            raise ValueError("duplicate pulse receipt")
        seen.add(pulse_id)
        if receipt["input_sha"] != expected_sha:
            stop_reason = "HEAD_DRIFT"
            rows.append({"pulse_id": pulse_id, "result": "BLOCKED",
                         "reason": stop_reason, "input_sha": receipt["input_sha"]})
            break
        if receipt["policy_sha256"] != plan["policy_sha256"]:
            stop_reason = "POLICY_DRIFT"
            rows.append({"pulse_id": pulse_id, "result": "BLOCKED",
                         "reason": stop_reason, "input_sha": receipt["input_sha"]})
            break
        result = receipt["result"]
        if result == "MEASURED":
            evidence_count += 1
        rows.append({
            "pulse_id": pulse_id,
            "result": result,
            "input_sha": receipt["input_sha"],
            "output_sha": receipt["output_sha"],
            "check_count": len(receipt["checks"]),
            "actions": receipt["actions"],
        })
        expected_sha = receipt["output_sha"]
        if receipt.get("major_blocker") or result == "BLOCKED":
            stop_reason = str(receipt.get("major_blocker") or "MATERIAL_BLOCKER")
            break
    evaluated = len(rows)
    return {
        "schema": REPORT_SCHEMA,
        "mission_id": plan["mission_id"],
        "wave_id": plan["wave_id"],
        "baseline_sha": plan["source_sha"],
        "last_reconciled_sha": expected_sha,
        "planned_pulses": 3,
        "evaluated_pulses": evaluated,
        "source_linked_measured_pulses": evidence_count,
        "independently_accepted_pulses": 0,
        "target_evaluated": evaluated == 3 and stop_reason is None,
        "next_pulse": None if stop_reason or evaluated == 3 else f"P{evaluated + 1}",
        "stop_reason": stop_reason,
        "merge_admission": "HOLD",
        "external_proof_required": True,
        "note": (
            "Receipt declarations do not authenticate GitHub, artifact bytes, "
            "independent review or merge admission."
        ),
        "pulses": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--receipts", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    receipts = json.loads(args.receipts.read_text(encoding="utf-8"))
    report = reconcile(plan, receipts)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "evaluated": report["evaluated_pulses"],
        "target_evaluated": report["target_evaluated"],
        "next": report["next_pulse"],
        "stop": report["stop_reason"],
        "merge_admission": report["merge_admission"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
