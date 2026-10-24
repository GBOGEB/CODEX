"""scripts/regen_missioncontrol_inventory.py must mirror what Mycelium CI checks."""
from __future__ import annotations

import fnmatch
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


KPI_SCRIPT = "scripts/measure_mycelium_kpis.py"
PROJECTION_SCRIPT = "scripts/project_recursive_control.py"
KPI_MANIFEST = "MANIFEST/MYCELIUM_KPI_MANIFEST.yaml"
INVENTORY_WORKFLOWS = ("missioncontrol-mycelium.yml", "missioncontrol-inventory-reconcile.yml", "missioncontrol-inventory-autoregen.yml")


def test_kpi_measurement_runs_after_receipts_and_is_a_tracked_output():
    script = _script()
    # KPIs measure every receipt written before them; only the recursive-control
    # projection, which ranks the KPI report, may run after.
    assert script.STEPS[-2:] == (KPI_SCRIPT, PROJECTION_SCRIPT)
    spec = importlib.util.spec_from_file_location("measure_mycelium_kpis", REPO_ROOT / KPI_SCRIPT)
    kpi = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(kpi)
    assert kpi.OUTPUT.relative_to(REPO_ROOT).as_posix() in script.TRACKED_OUTPUTS


def test_recursive_control_projection_is_tracked_and_rechecked():
    script = _script()
    spec = importlib.util.spec_from_file_location("project_recursive_control", REPO_ROOT / PROJECTION_SCRIPT)
    prc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(prc)
    assert {prc.OUTPUT.as_posix(), prc.PAGES_OUTPUT.as_posix()} <= set(script.TRACKED_OUTPUTS)
    verify = next(r for r in _runs("missioncontrol-mycelium.yml") if "cmp /tmp/registration_debt_classification.first.json" in r)
    assert f"python {PROJECTION_SCRIPT} --check" in verify


def test_mycelium_ci_rechecks_kpi_report_determinism():
    verify = next(r for r in _runs("missioncontrol-mycelium.yml") if "cmp /tmp/registration_debt_classification.first.json" in r)
    assert f"python {KPI_SCRIPT} --check" in verify


def test_inventory_workflows_trigger_on_every_kpi_input():
    manifest = yaml.safe_load((REPO_ROOT / KPI_MANIFEST).read_text(encoding="utf-8"))
    watched = [KPI_MANIFEST, KPI_SCRIPT, "docs/data/mycelium_kpi_measurement.json"]
    watched += [s["path"] for s in manifest["sources"].values()]
    for workflow in INVENTORY_WORKFLOWS:
        wf = yaml.safe_load((REPO_ROOT / ".github/workflows" / workflow).read_text(encoding="utf-8"))
        triggers = wf.get("on", wf.get(True))
        for event in ("push", "pull_request"):
            if event not in triggers:
                continue
            filters = triggers[event]["paths"]
            missing = [p for p in watched if not any(fnmatch.fnmatch(p, f) for f in filters)]
            assert not missing, (workflow, event, missing)


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


AUTOREGEN = ".github/workflows/missioncontrol-inventory-autoregen.yml"


def _autoregen() -> dict:
    return yaml.safe_load((REPO_ROOT / AUTOREGEN).read_text(encoding="utf-8"))


def test_autoregen_workflow_diffs_and_commits_exactly_the_tracked_outputs():
    blocks = [r.split("outputs=(", 1)[1].split(")", 1)[0] for r in _runs(Path(AUTOREGEN).name) if "outputs=(" in r]
    assert len(blocks) == 2
    for block in blocks:
        assert set(block.split()) == set(_script().TRACKED_OUTPUTS)


def test_autoregen_paths_cover_the_census_roots():
    contract = yaml.safe_load((REPO_ROOT / "mission_control/mycelium/executable_integration_value_contract.yaml").read_text(encoding="utf-8"))
    paths = _autoregen().get("on", _autoregen().get(True))["pull_request"]["paths"]
    for root in contract["migration"]["census_roots"]:
        assert f"{root}/**" in paths


def test_autoregen_workflow_cannot_retrigger_itself():
    wf = _autoregen()
    triggers = wf.get("on", wf.get(True))
    # Only pull_request: a GITHUB_TOKEN push to the PR branch creates no new
    # run, and the workflow_dispatch it sends targets Mycelium CI, not this file.
    assert set(triggers) == {"pull_request"}
    assert wf["permissions"] == {"contents": "read"}
    assert wf["concurrency"]["group"].endswith("${{ github.event.pull_request.number }}")
    steps = wf["jobs"]["autoregen"]["steps"]
    commit = next(s for s in steps if s.get("id") == "push")
    guard = next(s for s in steps if s.get("id") == "guard")
    subject = re.search(r'git commit -m "([^$"]+)', commit["run"]).group(1)
    pattern = re.search(r"grep -q '\^([^']+)'", guard["run"]).group(1)
    assert subject.startswith(pattern)
    dispatch = next(s for s in steps if "gh workflow run" in s.get("run", ""))
    assert "missioncontrol-mycelium.yml" in dispatch["run"]
    assert "--force" not in commit["run"]


def test_autoregen_pushes_only_for_same_repo_branches():
    job = _autoregen()["jobs"]["autoregen"]
    assert "head.repo.full_name == github.repository" in job["env"]["SAME_REPO"]
    by_name = {s.get("name"): s for s in job["steps"]}
    assert "env.SAME_REPO == 'true'" in by_name["Commit refreshed receipts to the PR branch"]["if"]
    fork = by_name["Fail with instructions (fork PR)"]
    assert "env.SAME_REPO != 'true'" in fork["if"]
    assert "python scripts/regen_missioncontrol_inventory.py" in fork["run"] and "exit 1" in fork["run"]


def test_autoregen_does_not_push_to_a_pr_that_merged_meanwhile():
    # The owner often merges within seconds; a push after that strands the
    # receipt commit on the branch. The PR state is read just before pushing.
    job = _autoregen()["jobs"]["autoregen"]
    assert job["permissions"]["pull-requests"] == "read"
    commit = next(s for s in job["steps"] if s.get("id") == "push")
    run = commit["run"]
    assert commit["env"]["PR_NUMBER"] == "${{ github.event.pull_request.number }}"
    assert run.index('pulls/${PR_NUMBER}" --jq .state') < run.index("git push")
    assert 'if [ "$state" != "open" ]' in run
