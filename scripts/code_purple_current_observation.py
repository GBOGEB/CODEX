"""Source-bound read-only current ABACUS observation, never a REX approval."""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import urllib.error
import urllib.request
from collections import Counter
from collections.abc import Callable
from pathlib import Path
from typing import Any

REPO = "GBOGEB/ABACUS"
BASE = "https://api.github.com"
OUTPUT = Path(__file__).resolve().parents[1] / "docs/data/code_purple_current_observation.json"
COHORT = (1876, 1875, 1873, 1872, 1871, 1869, 1859, 1858, 1857, 1856,
          1855, 1854, 1847, 1844, 1843, 1842, 1841, 1840, 1839, 1834)
SHA = re.compile(r"[0-9a-f]{40}\Z")
SCHEMA = "code-purple.current-observation/1.0"


def utc_now() -> str:
    return dt.datetime.now(dt.UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def github_get(path: str) -> Any:
    if not path.startswith(f"/repos/{REPO}/") or not re.fullmatch(
        r"/[A-Za-z0-9_./?=&%-]+", path
    ) or ".." in path:
        raise ValueError("GitHub API source must be ABACUS allowlisted")
    headers = {"Accept": "application/vnd.github+json",
               "X-GitHub-Api-Version": "2022-11-28",
               "User-Agent": "CODE-PURPLE-READONLY"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = "Bearer " + token
    request = urllib.request.Request(BASE + path, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            if response.geturl() != BASE + path:
                raise ValueError("unexpected redirect from GitHub API")
            return json.load(response)
    except (urllib.error.HTTPError, urllib.error.URLError) as error:
        raise RuntimeError("GitHub read-only observation unavailable") from error


def paged(get: Callable[[str], Any], route: str) -> list[dict]:
    rows: list[dict] = []
    for page in range(1, 21):
        batch = get(f"{route}&page={page}")
        if not isinstance(batch, list) or any(not isinstance(x, dict) for x in batch):
            raise ValueError("invalid GitHub paged list")
        rows.extend(batch)
        if len(batch) < 100:
            return rows
    raise ValueError("incomplete GitHub pagination")


def main_ref(get: Callable[[str], Any]) -> str:
    result = get(f"/repos/{REPO}/git/ref/heads/main")
    sha = (result.get("object") or {}).get("sha")
    if not isinstance(sha, str) or not SHA.fullmatch(sha):
        raise ValueError("invalid exact ABACUS main SHA")
    return sha


def _checks_once(get: Callable[[str], Any], sha: str) -> dict:
    rows = []
    total = None
    for page in range(1, 21):
        payload = get(f"/repos/{REPO}/commits/{sha}/check-runs?per_page=100&page={page}")
        if not isinstance(payload, dict) or not isinstance(payload.get("check_runs"), list):
            raise TypeError("invalid GitHub check response")
        total = payload.get("total_count") if total is None else total
        batch = payload["check_runs"]
        if any(x.get("head_sha") != sha for x in batch):
            raise ValueError("check SHA not bound to current main")
        rows.extend(batch)
        if len(batch) < 100:
            break
    else:
        raise ValueError("incomplete GitHub check census")
    if not isinstance(total, int) or total != len(rows):
        raise ValueError("check denominator mismatch")
    failures = []
    for check in rows:
        if check.get("conclusion") != "failure":
            continue
        url = check.get("html_url") or ""
        check_id = check.get("id") if isinstance(check.get("id"), int) else None
        first_red = None
        run_id = None
        step_state = "UNKNOWN_NO_AUTHENTICATED_JOB_STEP"
        # Bounded to 50 failures; never ingest logs or secrets. An Actions
        # job's failed step is an observation, not verified root cause.
        if check_id is not None and len(failures) < 50:
            try:
                job = get(f"/repos/{REPO}/actions/jobs/{check_id}")
                if job.get("id") != check_id:
                    raise ValueError("mismatched GitHub job identity")
                run_id = job.get("run_id") if isinstance(job.get("run_id"), int) else None
                steps = job.get("steps") or []
                first = next((x for x in sorted(
                    steps, key=lambda y: y.get("number") or 0
                ) if x.get("conclusion") == "failure"), None)
                if first is not None:
                    first_red = {
                        "step_number": first.get("number"),
                        "step_name": str(first.get("name") or "UNKNOWN")[:120],
                        "source_job_id": check_id,
                    }
                    step_state = "OBSERVED_FAILED_STEP_NOT_ROOT_CAUSE"
            except (RuntimeError, ValueError, AttributeError):
                step_state = "UNKNOWN_JOB_DETAIL_UNAVAILABLE"
        failures.append({
            "check_name": str(check.get("name") or "UNKNOWN")[:120],
            "check_id": check_id, "workflow_run_id": run_id,
            "source_url": url if url.startswith(f"https://github.com/{REPO}/") else None,
            "first_red_step": first_red, "step_evidence_state": step_state,
            "root_cause_class": "UNKNOWN_NO_CAUSAL_PROOF",
        })
    return {
        "population": "exact_main_check_runs", "denominator": total,
        "status_counts": dict(sorted(Counter(
            x.get("conclusion") or x.get("status") or "UNKNOWN" for x in rows
        ).items())),
        "failed_checks": failures[:50],
        "failure_list_truncated": len(failures) > 50,
        "verified_root_cause_count": None,
    }



def checks(get: Callable[[str], Any], sha: str) -> dict:
    """A moving check-run list cannot certify a complete denominator.

    Retry a bounded full exact-head enumeration; if new CI jobs keep
    entering, report UNKNOWN rather than a partial count or zero.
    This does not reduce any other security or governance requirement.
    """
    for _ in range(2):
        try:
            result = _checks_once(get, sha)
            result["census_state"] = "COMPLETE_AT_READBACK"
            return result
        except ValueError as error:
            if str(error) not in {
                "check denominator mismatch",
                "incomplete GitHub check census",
            }:
                raise
    return {
        "population": "exact_main_check_runs",
        "denominator": None,
        "status_counts": None,
        "failed_checks": [],
        "failure_list_truncated": None,
        "verified_root_cause_count": None,
        "census_state": "UNKNOWN_UNSTABLE_OR_BOUNDED_CENSUS",
    }


def observe(get: Callable[[str], Any] = github_get,
            clock: Callable[[], str] = utc_now) -> dict:
    start = clock()
    sha = main_ref(get)
    opened = paged(get, f"/repos/{REPO}/pulls?state=open&per_page=100")
    ids = [x.get("number") for x in opened]
    if any(not isinstance(n, int) for n in ids) or len(ids) != len(set(ids)):
        raise ValueError("invalid open PR population")
    merge_receipts = []
    for number in COHORT:
        pr = get(f"/repos/{REPO}/pulls/{number}")
        if pr.get("number") != number:
            raise ValueError("PR evidence identity mismatch")
        when = pr.get("merged_at")
        commit = pr.get("merge_commit_sha") if when else None
        if when and (not isinstance(commit, str) or not SHA.fullmatch(commit)):
            raise ValueError("unbound merged PR SHA")
        merge_receipts.append({
            "pr": number, "merged": when is not None,
            "merge_commit_sha": commit, "merged_at": when,
            "source_url": f"https://github.com/{REPO}/pull/{number}",
        })
    check_data = checks(get, sha)
    try:
        rule = get(f"/repos/{REPO}/rulesets/24494381")
        if rule.get("id") != 24494381 or not isinstance(rule.get("rules"), list):
            raise ValueError("ruleset identity/count unavailable")
        protection = {"id": 24494381, "enforcement": rule.get("enforcement"),
                      "rule_count": len(rule["rules"]), "state": "MEASURED"}
    except (RuntimeError, ValueError, AttributeError):
        protection = {"id": 24494381, "enforcement": None,
                      "rule_count": None, "state": "UNKNOWN_UNAVAILABLE"}
    if main_ref(get) != sha:
        raise ValueError("ABACUS main changed during observation")
    return {
        "schema": "code-purple.current-observation/1.0", "repo": REPO,
        "observed_started_at": start, "observed_at": clock(),
        "freshness_ttl_hours": 24, "observation_state": "READ_ONLY_NOT_ADMISSION",
        "source": {"main_sha": sha, "main_url": f"https://github.com/{REPO}/commit/{sha}",
                   "transport": "GITHUB_REST_READ_ONLY"},
        "current_prs": {
            "population": "repository_open_pull_requests", "open_count": len(ids),
            "open_numbers": sorted(ids),
            "source_url": f"https://github.com/{REPO}/pulls?q=is%3Apr+is%3Aopen",
        },
        "historical_cohort_current_disposition": {
            "population": "2026-10-12_original_20_pr_cohort",
            "denominator": len(COHORT),
            "merged_count": sum(p["merged"] for p in merge_receipts),
            "receipts": merge_receipts, "governed_merge_count": None,
            "governance_state": "POSTMERGE_REVIEW_NOT_AUDITED",
        },
        "current_main_checks": check_data, "main_ruleset": protection,
        "unmeasured": {
            "bd_queue_open": None, "bd_queue_closed": None,
            "root_cause_queue_open": None, "root_cause_queue_closed": None,
            "current_main_coverage": None, "current_diff_coverage": None,
            "authenticated_crew_runs": None, "measured_pca_score": None,
            "state": "UNKNOWN_NOT_ZERO",
        },
        "admission": {
            "independent_code_security_review": "NOT_PROVEN",
            "qps_consumer": "NOT_ADMITTED", "pages_byte_identity": "UNVERIFIED",
            "authority_transfer": False, "security_waiver": False,
            "formal_credit_delta": 0, "engineering_credit_delta": 0,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=OUTPUT)
    args = parser.parse_args()
    result = observe()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8")
    print("Captured ABACUS read-only current observation at " + result["source"]["main_sha"])


if __name__ == "__main__":
    main()
