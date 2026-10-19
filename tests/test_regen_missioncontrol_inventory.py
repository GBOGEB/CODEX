"""scripts/regen_missioncontrol_inventory.py must mirror what Mycelium CI checks."""
from __future__ import annotations

import importlib.util
import re
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]


def _script():
    spec = importlib.util.spec_from_file_location("regen_missioncontrol_inventory", REPO_ROOT / "scripts/regen_missioncontrol_inventory.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _runs(workflow: str) -> list[str]:
    wf = yaml.safe_load((REPO_ROOT / ".github/workflows" / workflow).read_text(encoding="utf-8"))
    return [step.get("run", "") for job in wf["jobs"].values() for step in job["steps"]]


def test_steps_match_mycelium_ci_order():
    runs = "\n".join(_runs("missioncontrol-mycelium.yml"))
    positions = [runs.index(f"python {step}") for step in _script().STEPS]
    assert positions == sorted(positions)


def test_preflight_and_verify_lists_match():
    script = _script()
    runs = _runs("missioncontrol-mycelium.yml")
    preflight = next(r for r in runs if "git diff --exit-code" in r and "First red" in r)
    assert set(re.findall(r"[\w./-]+\.json", preflight)) == set(script.PREFLIGHT_RECEIPTS)
    verify = next(r for r in runs if "cmp /tmp/registration_debt_classification.first.json" in r)
    last_diff = verify.strip().splitlines()[-1]
    assert set(re.findall(r"[\w./-]+\.json", last_diff)) == set(script.TRACKED_OUTPUTS)


def test_reconcile_workflow_commits_exactly_the_tracked_outputs():
    commit = next(r for r in _runs("missioncontrol-inventory-reconcile.yml") if "outputs=(" in r)
    block = commit.split("outputs=(", 1)[1].split(")", 1)[0]
    assert set(block.split()) == set(_script().TRACKED_OUTPUTS)


def test_reconcile_workflow_cannot_retrigger_itself():
    wf = yaml.safe_load((REPO_ROOT / ".github/workflows/missioncontrol-inventory-reconcile.yml").read_text(encoding="utf-8"))
    triggers = wf.get("on", wf.get(True))
    assert set(triggers) == {"push", "workflow_dispatch"}
    assert triggers["push"]["branches"] == ["main"]
    assert "pull_request_target" not in triggers and "workflow_run" not in triggers
