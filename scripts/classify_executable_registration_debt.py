from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "mission_control" / "mycelium" / "executable_value_report.json"
OUT = ROOT / "mission_control" / "mycelium" / "registration_debt_classification.json"
WORKFLOWS = ROOT / ".github" / "workflows"
TESTS = ROOT / "tests"

CLASSIFICATIONS = {
    "TESTED_ORPHAN",
    "LIBRARY_REFERENCE_ONLY",
    "PIPELINE_INTEGRATION_CANDIDATE",
    "ARCHIVE_REMOVE_CANDIDATE",
    "UNRESOLVED_REGISTRATION_DEBT",
}


def _test_stems(tests_root: Path) -> set[str]:
    return {
        path.stem.removeprefix("test_")
        for path in tests_root.rglob("test_*.py")
    }


def _iter_job_steps(payload: Any):
    if not isinstance(payload, dict):
        return
    jobs = payload.get("jobs")
    if not isinstance(jobs, dict):
        return
    for job in jobs.values():
        if not isinstance(job, dict):
            continue
        reusable = job.get("uses")
        if isinstance(reusable, str):
            yield reusable
        steps = job.get("steps")
        if not isinstance(steps, list):
            continue
        for step in steps:
            if not isinstance(step, dict):
                continue
            run = step.get("run")
            if isinstance(run, str):
                yield run
            uses = step.get("uses")
            if isinstance(uses, str):
                yield uses


def _executable_workflow_text(workflows_root: Path) -> str:
    chunks: list[str] = []
    for path in sorted(workflows_root.glob("*.y*ml")):
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
        chunks.extend(_iter_job_steps(payload) or [])
    return "\n".join(chunks)


def _source_label(report_path: Path) -> str:
    resolved = report_path.resolve()
    try:
        return str(resolved.relative_to(ROOT.resolve()))
    except ValueError:
        return str(resolved)


def classify(
    report_path: Path = REPORT,
    workflows_root: Path = WORKFLOWS,
    tests_root: Path = TESTS,
) -> dict[str, object]:
    report = json.loads(report_path.read_text(encoding="utf-8"))
    test_stems = _test_stems(tests_root)
    executable_text = _executable_workflow_text(workflows_root)
    rows = []
    for asset in report["inventory"]["unregistered_assets"]:
        stem = Path(asset).stem
        tested = stem in test_stems
        workflow_consumer = asset in executable_text
        if asset.startswith("tests/"):
            classification = "LIBRARY_REFERENCE_ONLY"
        elif asset.startswith(".github/workflows/"):
            classification = "PIPELINE_INTEGRATION_CANDIDATE"
        elif tested and not workflow_consumer:
            classification = "TESTED_ORPHAN"
        elif workflow_consumer:
            classification = "PIPELINE_INTEGRATION_CANDIDATE"
        else:
            classification = "UNRESOLVED_REGISTRATION_DEBT"
        rows.append({
            "asset": asset,
            "test_evidence": tested,
            "operational_edge": workflow_consumer,
            "downstream_consumer": "github_actions" if workflow_consumer else None,
            "execution_surface": "github_actions" if workflow_consumer else None,
            "outcome_value_evidence": None,
            "classification": classification,
        })
    counts = {
        name: sum(row["classification"] == name for row in rows)
        for name in sorted(CLASSIFICATIONS)
    }
    return {
        "schema_version": "0.2",
        "authority_class": "DERIVED_CENSUS",
        "authority_transfer": False,
        "source_report": _source_label(report_path),
        "candidate_count": len(rows),
        "classification_counts": counts,
        "candidates": rows,
    }


def main() -> int:
    payload = classify()
    OUT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload["classification_counts"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
