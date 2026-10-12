"""Fail-closed CODE PURPLE OVERTIME advisory planner tests."""
from __future__ import annotations

from copy import deepcopy

import pytest

from tools.code_purple_overtime import plan

SHA = "a" * 40


def task(name="scout", **changes):
    base = dict(
        id=name, state="QUEUED", kind="READ_ONLY_SCOUT", read_only=True,
        dependencies_complete=True, checkpoint_resumable=True,
        shared_write_lock=False, human_approval_required=False,
        sensitive_inputs=False, source_sha=SHA,
        receipt_target="receipts/scout.json", required_skills=["github_read"],
        estimated_seconds=12, convergence_gain=3.0, stability_gain=1.0,
        unblock_gain=0.5, max_queue_s=300, age_s=0,
    )
    base.update(changes)
    return base


def snapshot(items=None, workers=None, window=45):
    return {
        "schema": "code-purple.overtime.input/0.1",
        "capacity": {
            "capacity_proof_ref": "GBOGEB/CODEX/actions/runs/123",
            "critical_lane_resume_s": window,
            "free_workers": [
                {"id": "reader", "free": True, "observed": True,
                 "skills": ["github_read", "docs_links"]}
            ] if workers is None else workers,
        },
        "tasks": [task()] if items is None else items,
    }


def test_safe_readonly_task_proposes_plan_not_execution():
    result = plan(snapshot())
    assert result["status"] == "PLAN_READY_NOT_DISPATCHED"
    assert result["dispatch_plan_only"][0]["task"] == "scout"
    assert result["execution_claim"] == "NOT_DISPATCHED"
    assert result["security_exception"] is False
    assert result["authority_transfer"] is False


def test_missing_measured_capacity_holds():
    sample = snapshot()
    sample["capacity"]["capacity_proof_ref"] = None
    result = plan(sample)
    assert result["status"] == "HOLD_NO_MEASURED_CAPACITY"
    assert result["dispatch_plan_only"] == []


@pytest.mark.parametrize("change", [
    {"dependencies_complete": False},
    {"read_only": False},
    {"checkpoint_resumable": False},
    {"shared_write_lock": True},
    {"human_approval_required": True},
    {"sensitive_inputs": True},
    {"source_sha": "main"},
    {"receipt_target": ""},
    {"kind": "SECURITY_APPROVAL"},
    {"tags": ["RULESET_CHANGE"]},
    {"estimated_seconds": 200},
    {"state": "BLOCKED"},
])
def test_bypass_and_unready_work_never_assigned(change):
    result = plan(snapshot(items=[task(**change)]))
    assert result["dispatch_plan_only"] == []


def test_skill_mismatch_never_assigned():
    result = plan(snapshot(items=[task(required_skills=["licensed_hepak"])]))
    assert result["dispatch_plan_only"] == []
    assert result["blocked_by_skill_or_capacity"] == ["scout"]


def test_worker_must_be_observed_free():
    sample = snapshot()
    sample["capacity"]["free_workers"][0]["observed"] = False
    assert plan(sample)["dispatch_plan_only"] == []


def test_duplicate_task_rejected():
    with pytest.raises(ValueError):
        plan(snapshot(items=[task(), task()]))


def test_no_window_or_invalid_window_rejected():
    with pytest.raises(ValueError):
        plan(snapshot(window=0))
    with pytest.raises(ValueError):
        plan(snapshot(window=7200))


def test_same_task_only_once_for_many_workers():
    w = [{"id": "a", "free": True, "observed": True, "skills": ["github_read"]},
         {"id": "b", "free": True, "observed": True, "skills": ["github_read"]}]
    result = plan(snapshot(workers=w))
    assert len(result["dispatch_plan_only"]) == 1


def test_second_task_can_fill_second_worker_slot():
    w = [{"id": "a", "free": True, "observed": True, "skills": ["github_read"]},
         {"id": "b", "free": True, "observed": True, "skills": ["docs_links"]}]
    result = plan(snapshot(items=[
        task("first", required_skills=["github_read"]),
        task("second", required_skills=["docs_links"])
    ], workers=w))
    assert {x["task"] for x in result["dispatch_plan_only"]} == {"first", "second"}


def test_no_mutation_if_payload_exceeds_safe_budget():
    sample = snapshot()
    sample["tasks"] = [task(id=f"task{i}") for i in range(300)]
    with pytest.raises(ValueError):
        plan(sample)


def test_no_policy_approval_field_in_result():
    result = plan(snapshot())
    assert "owner_attestation" not in result
    assert result["merge_authority"] == "NONE"
