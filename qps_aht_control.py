"""CODEX-owned AHT check-control contract; vendored byte-for-byte by consumers.

Descriptive counts are not statistical hypothesis tests or release authority.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone

SCHEMA = "qps.aht-check-control/1.0.0"
FAILURES = ("failure", "cancelled", "timed_out", "action_required", "startup_failure", "stale")
PENDING = ("queued", "in_progress", "waiting", "requested", "pending")
COMPLETED = ("success", *FAILURES, "skipped", "neutral")
OUTCOMES = (*COMPLETED, *PENDING, "unknown")


def _integer(value: object, name: str, minimum: int = 0) -> int:
    if type(value) is not int or value < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}")
    return value


def evaluate(counts: dict, *, threshold: int = 1, coverage_complete: bool = False,
             unresolved_reviews: int | None = None) -> dict:
    """Fail closed on incomplete observations, manual concerns and pending work."""
    if not isinstance(counts, dict) or set(counts) - set(OUTCOMES):
        raise ValueError("unknown outcome keys")
    if type(coverage_complete) is not bool:
        raise ValueError("coverage_complete must be boolean")
    _integer(threshold, "threshold", 1)
    if unresolved_reviews is not None:
        _integer(unresolved_reviews, "unresolved_reviews")
    values = {key: _integer(counts.get(key, 0), key) for key in OUTCOMES}
    blockers = sum(values[key] for key in FAILURES)
    active = sum(values[key] for key in PENDING)
    completed = sum(values[key] for key in COMPLETED)
    decisive = values["success"] + blockers
    if blockers >= threshold:
        status = "THRESHOLD_BREACHED"
    elif blockers or unresolved_reviews:
        status = "HOLD"
    elif active:
        status = "PENDING"
    elif (not coverage_complete or unresolved_reviews is None or values["unknown"]
          or values["skipped"] or values["neutral"] or not values["success"]):
        status = "UNKNOWN"
    else:
        status = "CHECKS_CLEAR"
    return {
        "status": status,
        "threshold": {"blocking_completed_count": threshold, "reached": blockers >= threshold},
        "observed": {
            "counts": values, "total": sum(values.values()), "completed": completed,
            "decisive": decisive, "blocking_completed": blockers, "active": active,
            "success_rate": values["success"] / completed if completed else None,
            "decisive_success_rate": values["success"] / decisive if decisive else None,
            "failure_rate": blockers / decisive if decisive else None,
            "unresolved_reviews": unresolved_reviews, "coverage_complete": coverage_complete,
        },
        "release_accepted": False,
    }


def _timestamp(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timestamp requires timezone")
    return parsed.astimezone(timezone.utc)


def snapshot(repository: str, head_sha: str, observed_at: str, counts: dict,
             *, unit: str = "check", **policy) -> dict:
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
        raise ValueError("repository must be owner/name")
    if not re.fullmatch(r"[0-9a-f]{40}", head_sha):
        raise ValueError("head_sha must be full lowercase commit SHA")
    if unit not in ("check", "workflow_run"):
        raise ValueError("unsupported counting unit")
    _timestamp(observed_at)
    return {"schema": SCHEMA, "repository": repository, "head_sha": head_sha,
            "observed_at": observed_at, "unit": unit, "evidence_class": "DERIVED",
            **evaluate(counts, **policy)}


def digest(payload: dict) -> str:
    """SHA256 of canonical UTF-8 JSON; detached to avoid self-reference."""
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"),
                                     allow_nan=False).encode()).hexdigest()


def validate_snapshot(payload: dict, *, repository: str, head_sha: str,
                      expected_digest: str, now: str, max_age_seconds: int = 3600) -> str:
    """Validate external expected identity, digest, freshness and recomputed verdict."""
    _integer(max_age_seconds, "max_age_seconds", 1)
    if payload["repository"] != repository or payload["head_sha"] != head_sha:
        raise ValueError("stale or wrong repository/head binding")
    if digest(payload) != expected_digest:
        raise ValueError("SHA256 mismatch")
    age = (_timestamp(now) - _timestamp(payload["observed_at"])).total_seconds()
    if age < 0 or age > max_age_seconds:
        raise ValueError("stale or future observation")
    observed = payload["observed"]
    expected = snapshot(repository, head_sha, payload["observed_at"], observed["counts"],
                        unit=payload["unit"],
                        threshold=payload["threshold"]["blocking_completed_count"],
                        coverage_complete=observed["coverage_complete"],
                        unresolved_reviews=observed["unresolved_reviews"])
    if digest(payload) != digest(expected):
        raise ValueError("malformed contract or contradictory metrics/verdict")
    return payload["status"]


def render_pr_head(payload: dict) -> str:
    """A replaceable top-of-body block; does not change the PR title or source SHA."""
    obs = payload["observed"]
    return ("<!-- qps-aht-control:start -->\n"
            f"**AHT check control: {payload['status']}**\n\n"
            f"Observed {payload['observed_at']} on `{payload['head_sha']}`; "
            f"unit: {payload['unit']}. Threshold: "
            f"{payload['threshold']['blocking_completed_count']} blocking completed result(s).\n\n"
            "| Success | Blocking completed | Pending | Other/unknown | Reviews |\n"
            "|---:|---:|---:|---:|---:|\n"
            f"| {obs['counts']['success']} | {obs['blocking_completed']} | {obs['active']} | "
            f"{sum(obs['counts'][k] for k in ('skipped', 'neutral', 'unknown'))} | "
            f"{obs['unresolved_reviews'] if obs['unresolved_reviews'] is not None else 'unknown'} |\n\n"
            f"Snapshot SHA256: `{digest(payload)}`. "
            "CHECKS_CLEAR is scoped check evidence; child acceptance and runtime repeat remain separate.\n"
            "<!-- qps-aht-control:end -->\n")


def update_pr_body(body: str, payload: dict) -> str:
    """Replace only our marked block, preserving all human-authored content."""
    start, end = "<!-- qps-aht-control:start -->", "<!-- qps-aht-control:end -->"
    if body.count(start) != body.count(end) or body.count(start) > 1:
        raise ValueError("ambiguous PR control markers")
    if start in body:
        left, right = body.index(start), body.index(end)
        if right < left:
            raise ValueError("reversed PR control markers")
        body = body[:left] + body[right + len(end):]
    return render_pr_head(payload) + "\n" + body.lstrip("\n")
