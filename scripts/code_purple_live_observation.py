"""Read-only GitHub Actions observations for ABACUS CODE PURPLE.

An observation is not an admission, independent review, or REX receipt.
No GitHub write operations. Secrets and raw job logs are never exported.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

API = "https://api.github.com/repos/GBOGEB/ABACUS"
FULL_SHA = re.compile(r"^[0-9a-f]{40}$")
BASE = Path(__file__).resolve().parents[1]
OUT = BASE / "docs/data/code_purple_live_observation.json"


def require_sha(value: str) -> str:
    if not FULL_SHA.fullmatch(value):
        raise ValueError("expected full 40-character SHA")
    return value


def get_json(path: str, token: str | None = None) -> Any:
    if not path.startswith("/") or ".." in path or ("?" in path and not path.endswith("?per_page=100")):
        raise ValueError("untrusted API path")
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "CODEX-code-purple-readonly",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = "Bearer " + token
    req = urllib.request.Request(API + path, headers=headers, method="GET")
    with urllib.request.urlopen(req, timeout=20) as response:
        return json.load(response)


def normalize_check(item: dict[str, Any], sha: str) -> dict[str, Any]:
    if item.get("head_sha") != sha:
        raise ValueError("check belongs to different head")
    url = item.get("details_url")
    if not isinstance(url, str) or not url.startswith(
        "https://github.com/GBOGEB/ABACUS/"
    ):
        url = None
    return {
        "check_id": item.get("id"),
        "name": item.get("name"),
        "status": item.get("status"),
        "conclusion": item.get("conclusion"),
        "url": url,
        "started_at": item.get("started_at"),
        "completed_at": item.get("completed_at"),
    }


def collect(fetch: Any, head: str, main: str, now: str) -> dict[str, Any]:
    head, main = require_sha(head), require_sha(main)
    checks = fetch(f"/commits/{head}/check-runs?per_page=100")
    if not isinstance(checks, dict) or not isinstance(checks.get("check_runs"), list):
        raise ValueError("missing checks response")
    # The source API is paginated. Fail closed on truncation rather than
    # claiming a complete denominator based on a partial first page.
    if checks.get("total_count") != len(checks["check_runs"]):
        raise ValueError("check census incomplete; do not infer totals")
    records = [normalize_check(x, head) for x in checks["check_runs"]]
    if len({x["check_id"] for x in records}) != len(records):
        raise ValueError("duplicate check id")
    gate = [x for x in records if x["name"] == "PR Feedback Gate"]
    # Order by GitHub's temporal check identity; a new rerun supersedes
    # historical cancelled/pending/successful instances. Without a complete
    # started_at and distinct timestamp, the current gate remains UNKNOWN.
    chosen = None
    if gate and all(isinstance(x["started_at"], str) and x["started_at"]
                    for x in gate):
        latest = max(x["started_at"] for x in gate)
        leaders = [x for x in gate if x["started_at"] == latest]
        if len(leaders) == 1:
            chosen = leaders[0]
    status = (
        "UNKNOWN_UNORDERED_GATE" if gate and chosen is None
        else "UNKNOWN" if chosen is None
        else "SUCCESS_OBSERVED_UNVERIFIED"
        if chosen["conclusion"] == "success" else "BLOCKED_OR_PENDING"
    )
    conclusions = ["success", "failure", "cancelled", "skipped", "pending",
                   "timed_out", "neutral", "action_required", "stale",
                   "startup_failure"]
    counts = {key: 0 for key in conclusions}
    counts["other"] = 0
    for record in records:
        key = record["conclusion"]
        if key is None:
            key = "pending" if record["status"] != "completed" else "other"
        if key not in counts:
            key = "other"
        counts[key] += 1
    assert sum(counts.values()) == len(records)
    failed = [x for x in records if x["conclusion"] == "failure"]
    return {
        "schema": "code-purple.live-observation/1.0",
        "source_repo": "GBOGEB/ABACUS",
        "head_sha": head,
        "main_sha": main,
        "observed_at": now,
        "source_api": API,
        "check_census_complete": True,
        "observed_checks": len(records),
        "check_runs": records,
        "check_status_counts": counts,
        "observed_failed_check_ids": [x["check_id"] for x in failed],
        "first_red_step": None,
        "first_red_step_state": "UNKNOWN_NO_JOB_STEP_LOGS",
        "feedback_gate_observation": status,
        "current_feedback_gate_check_id": chosen["check_id"] if chosen else None,
        "independent_security_review": None,
        "authenticated_worker_rex": None,
        "main_coverage_pct": None,
        "pr_diff_coverage_pct": None,
        "bd_queue_open": None,
        "bd_queue_closed": None,
        "root_causes_open": None,
        "root_causes_closed": None,
        "merge_admission": "NOT_ASSERTED",
        "unknown_policy": "NULL_NOT_ZERO",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--head-sha", required=True)
    parser.add_argument("--main-sha", required=True)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args()
    # Verify main and head are complete SHA identifiers before network activity.
    require_sha(args.head_sha)
    require_sha(args.main_sha)
    token = os.environ.get("GITHUB_TOKEN")
    fetch = lambda path: get_json(path, token)
    head = fetch("/branches/main")
    if head.get("commit", {}).get("sha") != args.main_sha:
        raise SystemExit("ABACUS main moved; refuse stale observation")
    now = datetime.now(timezone.utc).isoformat()
    result = collect(fetch, args.head_sha, args.main_sha, now)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(f"Observed {result['observed_checks']} check runs; no admission asserted")


if __name__ == "__main__":
    main()
