from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from ruamel.yaml import YAML

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"
DEPLOY_ACTION = "actions/deploy-pages@v4"
REQUIRED_GROUP = "pages"
YAML_PARSER = YAML(typ="safe")


def _display_path(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _group(value: Any) -> str | None:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        group = value.get("group")
        return str(group) if group is not None else None
    return None


def _job_uses_deploy_pages(job: Any) -> bool:
    if not isinstance(job, dict):
        return False
    for step in job.get("steps", []) or []:
        if isinstance(step, dict) and str(step.get("uses", "")).startswith(DEPLOY_ACTION):
            return True
    return False


def audit(workflows_dir: Path = WORKFLOWS) -> list[str]:
    errors: list[str] = []
    deployer_count = 0
    for path in sorted(list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml"))):
        raw = path.read_text(encoding="utf-8", errors="replace")
        # This is a Pages-ownership audit, not a general workflow-YAML linter.
        # Parse failures remain fail-closed only for files that can deploy the
        # shared Pages endpoint; unrelated legacy workflow syntax is out of scope.
        if DEPLOY_ACTION not in raw:
            continue
        label = _display_path(path)
        try:
            doc = YAML_PARSER.load(raw) or {}
        except Exception as exc:  # pragma: no cover - surfaced as audit failure
            errors.append(f"{label}: Pages-deployer YAML parse failed: {exc}")
            continue
        if not isinstance(doc, dict):
            errors.append(f"{label}: Pages-deployer YAML root is not a mapping")
            continue

        top_group = _group(doc.get("concurrency"))
        jobs = doc.get("jobs", {}) or {}
        if not isinstance(jobs, dict):
            errors.append(f"{label}: Pages-deployer jobs block is not a mapping")
            continue

        deploy_jobs = [(name, job) for name, job in jobs.items() if _job_uses_deploy_pages(job)]
        if not deploy_jobs:
            errors.append(f"{label}: contains {DEPLOY_ACTION} but no parseable deploy-pages job")
            continue
        deployer_count += len(deploy_jobs)

        for job_name, job in deploy_jobs:
            job_group = _group(job.get("concurrency")) if isinstance(job, dict) else None
            if REQUIRED_GROUP not in {top_group, job_group}:
                errors.append(
                    f"{label}::{job_name}: deploy-pages job is outside shared "
                    f"concurrency group '{REQUIRED_GROUP}' (top={top_group!r}, job={job_group!r})"
                )

    if deployer_count == 0:
        errors.append("no actions/deploy-pages@v4 jobs found; audit cannot prove Pages ownership topology")
    return errors


def main() -> int:
    errors = audit()
    if errors:
        print("PAGES DEPLOYMENT CONCURRENCY AUDIT FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    print("PAGES DEPLOYMENT CONCURRENCY AUDIT PASSED")
    print(f"required_group={REQUIRED_GROUP}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
