#!/usr/bin/env python3
"""Code Purple semantic census deltas (no network, no GitHub push, no approval).

Reads two already controlled observations. Emits only changed fields and
tombstones, with exact identities and SHA-256 replay guards. GitHub Pages may
publish the small delta alongside existing governed products through its one
canonical writer; it does not support delta-only artifact deployment.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

FULL_SHA = re.compile(r"^[0-9a-f]{40}$")
ALLOWED_RECORD = {
    "id", "kind", "name", "status", "conclusion", "run_id",
    "run_attempt", "job_id", "evidence_url", "duration_seconds",
}
ALLOWED_MISSION = {
    "goal", "dov", "todo_open", "todo_closed", "blocked",
    "progress_numerator", "progress_denominator", "evidence_ref",
}
STATE_FIELDS = {"repo", "scope", "source_sha", "mission", "records"}


def canonical(obj: Any) -> bytes:
    return json.dumps(obj, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("ascii")


def digest(obj: Any) -> str:
    return hashlib.sha256(canonical(obj)).hexdigest()


def validate(raw: dict[str, Any]) -> dict[str, Any]:
    """Build a canonical, public-safe semantic state; omit volatile observed_at."""
    if not isinstance(raw, dict) or raw.get("schema") != "code-purple.census.snapshot/1":
        raise ValueError("snapshot schema missing or unsupported")
    if not isinstance(raw.get("repo"), str) or not raw["repo"].startswith("GBOGEB/"):
        raise ValueError("repo must be an explicit GBOGEB repository")
    if not isinstance(raw.get("scope"), str) or not raw["scope"]:
        raise ValueError("scope is required")
    if not isinstance(raw.get("source_sha"), str) or not FULL_SHA.fullmatch(raw["source_sha"]):
        raise ValueError("source_sha must bind a full lowercase commit SHA")
    if set(raw) - (STATE_FIELDS | {"schema", "observed_at"}):
        raise ValueError("unexpected fields: refuse accidental data disclosure")
    mission = raw.get("mission", {})
    if not isinstance(mission, dict) or set(mission) - ALLOWED_MISSION:
        raise ValueError("mission must contain only allowed public projection fields")
    for key, value in mission.items():
        if key in {"todo_open", "todo_closed", "blocked", "progress_numerator", "progress_denominator"}:
            if type(value) is not int or value < 0:
                raise ValueError("mission counters must be nonnegative integers")
        elif not isinstance(value, str) or len(value) > 240:
            raise ValueError("mission labels must be bounded strings")
    if {"progress_numerator", "progress_denominator"} <= set(mission):
        if mission["progress_denominator"] < 1 or mission["progress_numerator"] > mission["progress_denominator"]:
            raise ValueError("invalid measured mission denominator")
    records = raw.get("records")
    if not isinstance(records, list):
        raise ValueError("records must be a list; absent census is not an empty census")
    indexed: dict[str, dict[str, Any]] = {}
    for row in records:
        if not isinstance(row, dict) or set(row) - ALLOWED_RECORD:
            raise ValueError("record contains unsupported data or raw log content")
        key = row.get("id")
        if not isinstance(key, str) or not key or key in indexed:
            raise ValueError("record identifiers must be nonempty and unique")
        if row.get("run_attempt") is not None and (type(row["run_attempt"]) is not int or row["run_attempt"] < 1):
            raise ValueError("run_attempt must be a positive integer")
        for field, value in row.items():
            if field in {"run_id", "job_id"}:
                if type(value) is not int or value < 0:
                    raise ValueError("run/job identifiers must be nonnegative integers")
            elif field == "run_attempt":
                continue
            elif field == "duration_seconds":
                if type(value) not in (int, float) or value < 0 or value != value:
                    raise ValueError("duration must be finite nonnegative numeric data")
            elif not isinstance(value, str) or len(value) > 240:
                raise ValueError("record string values must be bounded")
        if row.get("evidence_url") and not row["evidence_url"].startswith("https://github.com/GBOGEB/"):
            raise ValueError("only public GitHub repository evidence URLs may be projected")
        indexed[key] = dict(row)
    return {
        "repo": raw["repo"], "scope": raw["scope"],
        "source_sha": raw["source_sha"], "mission": mission,
        "records": {k: indexed[k] for k in sorted(indexed)},
    }


def field_patch(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    return {
        "set": {k: after[k] for k in sorted(after) if k not in before or before[k] != after[k]},
        "unset": sorted(k for k in before if k not in after),
    }


def make_delta(previous: dict[str, Any], current: dict[str, Any]) -> dict[str, Any]:
    left, right = validate(previous), validate(current)
    if left["repo"] != right["repo"] or left["scope"] != right["scope"]:
        raise ValueError("different repo/scope; require independent baseline")
    prior = left["records"]
    present = right["records"]
    added = {k: present[k] for k in sorted(set(present) - set(prior))}
    removed = sorted(set(prior) - set(present))
    updated = {
        k: field_patch(prior[k], present[k])
        for k in sorted(set(prior) & set(present))
        if prior[k] != present[k]
    }
    mission_patch = field_patch(left["mission"], right["mission"])
    head_changed = left["source_sha"] != right["source_sha"]
    changed = bool(added or removed or updated or mission_patch["set"] or mission_patch["unset"] or head_changed)
    payload = {
        "schema": "code-purple.census.delta/1",
        "repo": right["repo"], "scope": right["scope"],
        "base_source_sha": left["source_sha"],
        "target_source_sha": right["source_sha"],
        "base_digest": digest(left), "target_digest": digest(right),
        "status": "DELTA_READY" if changed else "NO_CHANGE",
        "head_changed": head_changed,
        "comparability": "CROSS_HEAD_REBASELINE" if head_changed else "SAME_HEAD",
        "records": {"added": added, "updated": updated, "removed": removed},
        "mission": mission_patch,
        "counts": {
            "previous_records": len(prior), "current_records": len(present),
            "added": len(added), "updated": len(updated), "removed": len(removed),
        },
        "analytics_credit": "WITHHELD_NO_INDEPENDENT_ITERATION_DENOMINATOR",
        "repo_admission": "NOT_GRANTED_BY_CENSUS",
        "authority_transfer": False, "formal_credit_delta": 0,
    }
    payload["delta_digest"] = digest(payload)
    return payload


def apply_delta(previous: dict[str, Any], delta: dict[str, Any]) -> dict[str, Any]:
    state = validate(previous)
    if delta.get("schema") != "code-purple.census.delta/1":
        raise ValueError("unknown delta schema")
    expected = dict(delta)
    signed = expected.pop("delta_digest", None)
    if signed != digest(expected) or delta.get("base_digest") != digest(state):
        raise ValueError("delta or baseline digest mismatch")
    if delta.get("repo") != state["repo"] or delta.get("scope") != state["scope"]:
        raise ValueError("cross-domain replay forbidden")
    if delta.get("base_source_sha") != state["source_sha"]:
        raise ValueError("stale source SHA")
    target_sha = delta.get("target_source_sha")
    if not isinstance(target_sha, str) or not FULL_SHA.fullmatch(target_sha):
        raise ValueError("invalid target SHA")
    result = {
        "repo": state["repo"], "scope": state["scope"], "source_sha": target_sha,
        "mission": dict(state["mission"]),
        "records": {k: dict(v) for k, v in state["records"].items()},
    }
    for key in delta["mission"]["unset"]:
        result["mission"].pop(key)
    result["mission"].update(delta["mission"]["set"])
    for key in delta["records"]["removed"]:
        result["records"].pop(key)
    for key, row in delta["records"]["added"].items():
        if key in result["records"]:
            raise ValueError("replay added record already exists")
        result["records"][key] = dict(row)
    for key, patch in delta["records"]["updated"].items():
        if key not in result["records"]:
            raise ValueError("update refers to missing record")
        for field in patch["unset"]:
            result["records"][key].pop(field)
        result["records"][key].update(patch["set"])
    if digest(result) != delta["target_digest"]:
        raise ValueError("target hash mismatch after replay")
    return result


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--previous", type=Path, required=True)
    p.add_argument("--current", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    # On missing prior data fail closed: no speculative zero baseline.
    previous = json.loads(args.previous.read_text(encoding="utf-8"))
    current = json.loads(args.current.read_text(encoding="utf-8"))
    delta = make_delta(previous, current)
    apply_delta(previous, delta)  # self-test replay before emission
    if delta["status"] == "NO_CHANGE":
        print("NO_CHANGE: no publication payload written")
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(delta, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print("DELTA_READY", delta["delta_digest"], args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
