from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

from ruamel.yaml import YAML
from ruamel.yaml.error import YAMLError

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"
DEPLOY_ACTION_PREFIX = "actions/deploy-pages@"
CANONICAL_WORKFLOW = ".github/workflows/pages.yml"
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


def _deploy_steps(job: Any) -> list[str]:
    if not isinstance(job, dict):
        return []
    found: list[str] = []
    for step in job.get("steps", []) or []:
        if isinstance(step, dict):
            uses = str(step.get("uses", ""))
            if uses.startswith(DEPLOY_ACTION_PREFIX):
                found.append(uses)
    return found


def _pages_write_enabled(value: Any) -> bool:
    if isinstance(value, str):
        return value.strip().lower() == "write-all"
    if isinstance(value, dict):
        return str(value.get("pages", "")).strip().lower() == "write"
    return False


def _raw_pages_sensitive(raw: str) -> bool:
    return (
        DEPLOY_ACTION_PREFIX in raw
        or re.search(
            r"(?mi)^\s*permissions\s*:\s*['\"]?write-all['\"]?\s*(?:#.*)?$",
            raw,
        )
        is not None
        or re.search(
            r"(?mi)^\s*pages\s*:\s*['\"]?write['\"]?\s*(?:[,}}#].*)?$",
            raw,
        )
        is not None
        or re.search(
            r"(?mi)^\s*permissions\s*:\s*\{[^\n]*\bpages\s*:\s*['\"]?write['\"]?(?:\s*(?:[,}}#].*)?)?$",
            raw,
        )
        is not None
    )


def audit(workflows_dir: Path = WORKFLOWS) -> list[str]:
    errors: list[str] = []
    canonical_deployers = 0

    canonical_path = (workflows_dir / "pages.yml").resolve()

    for path in sorted(list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml"))):
        raw = path.read_text(encoding="utf-8", errors="replace")
        label = _display_path(path)
        try:
            doc = YAML_PARSER.load(raw) or {}
        except YAMLError as exc:
            # Unrelated malformed legacy workflows are outside this ownership audit.
            # A malformed file that still advertises Pages write/deploy authority fails closed.
            if _raw_pages_sensitive(raw):
                errors.append(f"{label}: Pages ownership YAML parse failed: {exc}")
            continue
        if not isinstance(doc, dict):
            errors.append(f"{label}: Pages ownership YAML root is not a mapping")
            continue

        jobs = doc.get("jobs", {}) or {}
        if not isinstance(jobs, dict):
            errors.append(f"{label}: jobs block is not a mapping")
            continue

        deploy_jobs = []
        for job_name, job in jobs.items():
            actions = _deploy_steps(job)
            if actions:
                deploy_jobs.append((job_name, job, actions))

        top_pages_write = _pages_write_enabled(doc.get("permissions"))
        job_pages_write = any(
            _pages_write_enabled(job.get("permissions"))
            for job in jobs.values()
            if isinstance(job, dict)
        )

        is_canonical = path.resolve() == canonical_path
        if not is_canonical:
            if deploy_jobs:
                for job_name, _job, actions in deploy_jobs:
                    errors.append(
                        f"{label}::{job_name}: non-canonical workflow may not deploy shared Pages "
                        f"(actions={actions!r}); canonical={CANONICAL_WORKFLOW}"
                    )
            if top_pages_write or job_pages_write:
                errors.append(
                    f"{label}: non-canonical workflow may not hold pages:write permission; "
                    f"canonical={CANONICAL_WORKFLOW}"
                )
            continue

        canonical_deployers += len(deploy_jobs)
        if len(deploy_jobs) != 1:
            errors.append(
                f"{label}: canonical workflow must contain exactly one deploy-pages job, "
                f"observed={len(deploy_jobs)}"
            )
        if not (top_pages_write or job_pages_write):
            errors.append(f"{label}: canonical workflow is missing pages:write permission")

        top_group = _group(doc.get("concurrency"))
        for job_name, job, _actions in deploy_jobs:
            job_group = _group(job.get("concurrency")) if isinstance(job, dict) else None
            if REQUIRED_GROUP not in {top_group, job_group}:
                errors.append(
                    f"{label}::{job_name}: canonical deploy-pages job is outside "
                    f"concurrency group {REQUIRED_GROUP!r}"
                )

    if canonical_deployers != 1:
        errors.append(
            f"canonical Pages writer count must be exactly 1; observed={canonical_deployers}"
        )
    return errors


def main() -> int:
    errors = audit()
    if errors:
        print("PAGES SINGLE-WRITER OWNERSHIP AUDIT FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    print("PAGES SINGLE-WRITER OWNERSHIP AUDIT PASSED")
    print(f"canonical_workflow={CANONICAL_WORKFLOW}")
    print(f"required_group={REQUIRED_GROUP}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
