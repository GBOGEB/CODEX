"""Regenerate the MissionControl executable-value receipts in one command.

Runs the canonical sequence that MissionControl Mycelium CI runs before its
"Preflight generated-value parity" step, then reports which tracked receipts
changed. Use it in any PR that adds or removes a test, workflow, script or
module:

    python scripts/regen_missioncontrol_inventory.py          # regenerate in place
    python scripts/regen_missioncontrol_inventory.py --check  # exit 1 on drift

The same script runs after every push to main in
.github/workflows/missioncontrol-inventory-reconcile.yml.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

# Order matches .github/workflows/missioncontrol-mycelium.yml.
STEPS = (
    "scripts/analyze_missioncontrol_logs.py",
    "scripts/build_missioncontrol_metrics.py",
    "scripts/validate_missioncontrol_mycelium.py",
    "scripts/validate_executable_integration_value.py",
    "scripts/consume_executable_value_report.py",
    "scripts/classify_executable_registration_debt.py",
    # Measures KPIs over the receipts the steps above just wrote.
    "scripts/measure_mycelium_kpis.py",
    # Last: ranks the KPI report back into control horizons (RCH-04).
    "scripts/project_recursive_control.py",
)

# Receipts checked by the preflight step (git diff --exit-code).
PREFLIGHT_RECEIPTS = (
    "mission_control/mycelium/executable_value_report.json",
    "docs/data/missioncontrol_executable_value_report.json",
    "mission_control/mycelium/executable_value_control_observation.json",
)

# All tracked materializations checked by "Verify deterministic materializations".
TRACKED_OUTPUTS = PREFLIGHT_RECEIPTS + (
    "mission_control/mycelium/metrics_snapshot.json",
    "docs/data/missioncontrol_metrics.json",
    "mission_control/mycelium/log_analysis.json",
    "docs/data/missioncontrol_log_analysis.json",
    "docs/data/mycelium_kpi_measurement.json",
    "mission_control/mycelium/recursive_control_projection.json",
    "docs/data/missioncontrol_recursive_control_projection.json",
)

# Written by the classify step but not tracked; CI regenerates it.
UNTRACKED_BYPRODUCT = "mission_control/mycelium/registration_debt_classification.json"

REPORT = "mission_control/mycelium/executable_value_report.json"


def _git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=REPO_ROOT, check=True, capture_output=True, text=True).stdout


def _unregistered(text: str) -> set[str]:
    return set(json.loads(text)["inventory"]["unregistered_assets"])


def regenerate() -> None:
    for step in STEPS:
        result = subprocess.run([sys.executable, step], cwd=REPO_ROOT, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            sys.stderr.write(result.stdout + result.stderr)
            raise SystemExit(f"FAILED: {step} exited {result.returncode}")
    byproduct = REPO_ROOT / UNTRACKED_BYPRODUCT
    tracked = _git("ls-files", UNTRACKED_BYPRODUCT).strip()
    if byproduct.exists() and not tracked:
        byproduct.unlink()


def changed_outputs() -> list[str]:
    return [p for p in TRACKED_OUTPUTS if _git("diff", "--name-only", "--", p).strip()]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="exit 1 if any tracked receipt changes")
    args = parser.parse_args(argv)

    before = _unregistered(_git("show", f"HEAD:{REPORT}"))
    regenerate()
    after = _unregistered((REPO_ROOT / REPORT).read_text(encoding="utf-8"))
    changed = changed_outputs()

    print(json.dumps({
        "changed_outputs": changed,
        "unregistered_added": sorted(after - before),
        "unregistered_removed": sorted(before - after),
        "unregistered_count": len(after),
    }, indent=2))
    if args.check and changed:
        print("DRIFT: run `python scripts/regen_missioncontrol_inventory.py` and commit the changed receipts.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
