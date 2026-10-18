"""W31 read-only, exact-head GitHub run census and non-compensating wave controller.

Input is a frozen, caller-acquired GitHub readback. This module never polls,
dispatches, merges, suppresses a gate, or infers formal review/root closure.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

SCHEMA = "codepurple.mycelium.w31.fresh-census.v1"
AXES = ("source_coverage", "adversarial_penetration", "cross_module_integration",
        "platform_runner_reach", "causal_defect_detection")
SHA40 = re.compile(r"[0-9a-f]{40}\Z")
SHA64 = re.compile(r"[0-9a-f]{64}\Z")
ACTIVE = {"queued", "pending", "in_progress", "requested", "waiting"}
FINISHED = {"success", "failure", "cancelled", "skipped", "timed_out", "neutral",
            "action_required", "stale", "startup_failure"}
REPOS = {"GBOGEB/ABACUS", "GBOGEB/CODEX"}


def need(p, why):
    if not p:
        raise ValueError(why)


def canonical(data):
    return (json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
            + "\n").encode("utf-8")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def require_sha(value, name):
    need(type(value) is str and bool(SHA40.fullmatch(value)), name)


def snapshot_view(data):
    need(type(data) is dict and data.get("schema") == SCHEMA, "BAD_SCHEMA")
    guard = data.get("governance", {})
    need(guard == {"merge_admission": "HOLD", "mutation_enabled": False,
                   "authority_transfer": False, "formal_root_closures": None},
         "AUTHORITY_PROMOTION")
    snapshots = data.get("snapshots")
    need(type(snapshots) is list and snapshots, "EMPTY_CENSUS")
    seen_repos = set()
    result = []
    max_queue_ratio = 0.0
    for s in snapshots:
        repo = s.get("repo")
        need(repo in REPOS and repo not in seen_repos, "DUPLICATE_OR_UNKNOWN_REPO")
        seen_repos.add(repo)
        require_sha(s.get("head_sha"), "UNPINNED_MAIN_HEAD")
        rows = s.get("runs")
        total = s.get("reported_total")
        need(type(rows) is list and type(total) is int and total >= len(rows),
             "BAD_RUN_POPULATION")
        seen_attempts = {}
        latest = {}
        for raw in rows:
            need(type(raw) is dict and type(raw.get("id")) is int and raw["id"] > 0
                 and type(raw.get("attempt")) is int and raw["attempt"] > 0,
                 "BAD_RUN_ID_ATTEMPT")
            need(raw.get("head_sha") == s["head_sha"], "STALE_OR_CROSS_HEAD_RUN")
            status, conclusion = raw.get("status"), raw.get("conclusion")
            need((status in ACTIVE and conclusion is None) or
                 (status == "completed" and conclusion in FINISHED),
                 "FAKE_NATIVE_TERMINAL")
            ident = (raw["id"], raw["attempt"])
            if ident in seen_attempts:
                need(seen_attempts[ident] == raw, "CONFLICTING_REPLAY")
                continue
            seen_attempts[ident] = raw
            other = latest.get(raw["id"])
            if other is None or raw["attempt"] > other["attempt"]:
                latest[raw["id"]] = raw
        need(total >= len(latest), "OVERSTATED_RUN_COVERAGE")
        counts = Counter(r["status"] if r["status"] != "completed"
                         else "completed/" + r["conclusion"] for r in latest.values())
        active = sum(counts[x] for x in ACTIVE)
        observed = len(latest)
        ratio = active / observed if observed else None
        if ratio is not None:
            max_queue_ratio = max(max_queue_ratio, ratio)
        result.append({"repo": repo, "exact_main_sha": s["head_sha"],
                       "reported_runs": total, "observed_distinct_runs": observed,
                       "observed_attempt_instances": len(seen_attempts),
                       "unknown_tail": total-observed,
                       "population_complete": total == observed,
                       "latest_attempt_statuses": dict(sorted(counts.items())),
                       "observed_nonterminal": active,
                       "observed_nonterminal_ratio": None if ratio is None
                           else round(ratio, 6),
                       "source": "GITHUB_ACTIONS_RUN_API_FIRST_PAGE_READBACK"})
    return result, max_queue_ratio


def evaluate_axis(observations, *, min_flat_deltas=3):
    """One-axis stability requires 4+ qualified comparable observations.

    Flat values below target trigger source-owner pivot, not false closure.
    Different SHA/scope/denominator is not a valid coverage delta.
    """
    need(type(min_flat_deltas) is int and min_flat_deltas >= 3,
         "UNSAFE_CONVERGENCE_THRESHOLD")
    need(type(observations) is list, "BAD_AXIS_SERIES")
    if not observations:
        return {"state": "UNKNOWN", "matched_deltas": [], "flat_deltas": 0}
    valid = []
    for point in observations:
        need(type(point) is dict, "BAD_AXIS_POINT")
        require_sha(point.get("source_sha"), "AXIS_SOURCE_NOT_PINNED")
        need(type(point.get("scope_sha256")) is str and
             bool(SHA64.fullmatch(point["scope_sha256"])), "AXIS_SCOPE_UNPINNED")
        num, den = point.get("numerator"), point.get("denominator")
        need(type(num) is int and type(den) is int and 0 <= num <= den and den > 0,
             "BAD_AXIS_DENOMINATOR")
        need(point.get("evidence") == "TERMINAL_NATIVE_ACCEPTED", "UNVERIFIED_AXIS_POINT")
        valid.append(point)
    current = valid[-1]
    key = (current["source_sha"], current["scope_sha256"], current["denominator"])
    if any((x["source_sha"], x["scope_sha256"], x["denominator"]) != key for x in valid):
        return {"state": "UNCOMPARABLE", "matched_deltas": [], "flat_deltas": 0}
    deltas = [b["numerator"]-a["numerator"] for a,b in zip(valid,valid[1:])]
    if any(d < 0 for d in deltas):
        return {"state": "REGRESSION", "matched_deltas": deltas, "flat_deltas": 0}
    flat = 0
    for d in reversed(deltas):
        if d:
            break
        flat += 1
    if deltas and deltas[-1] > 0:
        state = "EXPAND_MEASURED"
    elif flat >= min_flat_deltas:
        state = ("STABLE_LOCAL_TARGET" if current["numerator"] == current["denominator"]
                 else "REDIRECT_PLATEAU_BELOW_TARGET")
    else:
        state = "REPEAT_BOUNDED"
    return {"state": state, "matched_deltas": deltas,
            "flat_deltas": flat, "latest": {"numerator": current["numerator"],
                                           "denominator": current["denominator"]}}


def historical_roots(data):
    """Group manifestations by a declared signature, never award root closure."""
    cohorts = data.get("historical_job_manifestations", [])
    need(type(cohorts) is list, "BAD_ROOT_INPUT")
    seen = {}
    fingerprints = defaultdict(lambda: {"jobs": set(), "cells": set(), "runs": set()})
    for r in cohorts:
        need(type(r) is dict and r.get("repo") in REPOS and
             type(r.get("run_id")) is int and r["run_id"] > 0 and
             type(r.get("attempt")) is int and r["attempt"] > 0 and
             type(r.get("job_id")) is int and r["job_id"] > 0 and
             type(r.get("root_signature")) is str and r["root_signature"] and
             type(r.get("cell")) is str and r["cell"], "BAD_MANIFESTATION")
        key = (r["repo"], r["run_id"], r["attempt"], r["job_id"])
        if key in seen:
            need(seen[key] == r, "CONFLICTING_ROOT_REPLAY")
            continue
        seen[key] = r
        f = fingerprints[(r["repo"], r["root_signature"])]
        f["jobs"].add(r["job_id"])
        f["cells"].add(r["cell"])
        f["runs"].add((r["run_id"], r["attempt"]))
    return {"observed_job_manifestations": len(seen),
            "distinct_first_red_signatures": len(fingerprints),
            "roots": [{"repo": repo, "signature": sig,
                       "job_manifestations": len(v["jobs"]),
                       "distinct_cells": len(v["cells"]),
                       "run_attempt_instances": len(v["runs"]),
                       "owner_accepted_closure": None}
                      for (repo,sig),v in sorted(fingerprints.items())]}


def report(data):
    census, pressure = snapshot_view(data)
    axes = data.get("axis_observations", {})
    need(type(axes) is dict and set(axes) == set(AXES), "FIVE_AXIS_OMISSION")
    statuses = {axis: evaluate_axis(axes[axis]) for axis in AXES}
    # Queue pressure is observed, not a proof of runner exhaustion; plan is
    # read-only. Never fan out a saturated current-head queue by default.
    parallelism = 1 if pressure >= 0.80 else 2 if any(
        x["state"] == "EXPAND_MEASURED" for x in statuses.values()) else 1
    return {"schema":"codepurple.mycelium.w31.report.v1",
            "evidence_class": "FROZEN_GITHUB_READBACK_NOT_LIVE_SUBSCRIPTION",
            "source_digest": digest(canonical(data)),
            "main_census": census, "five_axes": statuses,
            "shared_first_red": historical_roots(data),
            "scheduler_proposal": {"max_new_parallel_source_lanes": parallelism,
                                   "observed_peak_queue_ratio": round(pressure, 6),
                                   "mutation_enabled": False,
                                   "reason": "QUEUE_AWARE_READ_ONLY_DO_NOT_RETRY_PENDING"},
            "governance": {"merge_admission": "HOLD", "authority_transfer": False,
                           "human_approval": None, "accepted_roots": None,
                           "authenticated_dispatch": None}}


def write(data, folder, *, head, run_id=None, attempt=None):
    require_sha(head, "CANDIDATE_HEAD_NOT_PINNED")
    for x in (run_id,attempt):
        need(x is None or type(x) is int and x > 0,"INVALID_RUN_ATTEMPT")
    folder.mkdir(parents=True,exist_ok=True)
    raw = canonical(report(data))
    (folder/"W31_CENSUS_REPORT.json").write_bytes(raw)
    receipt = {"schema":"codepurple.mycelium.w31.sha256.v1",
               "candidate_head":head,"run_id":run_id,"attempt":attempt,
               "source_digest":digest(canonical(data)),
               "admission":"HOLD","mutation_enabled":False,
               "files":{"W31_CENSUS_REPORT.json":digest(raw)}}
    (folder/"W31_SHA256.json").write_bytes(canonical(receipt))
    return receipt


def verify(folder, *, head):
    receipt = json.loads((folder/"W31_SHA256.json").read_bytes())
    need(receipt.get("candidate_head") == head and receipt.get("admission")=="HOLD"
         and receipt.get("mutation_enabled") is False, "RECEIPT_PROMOTION")
    need(set(receipt.get("files",{})) == {"W31_CENSUS_REPORT.json"},"BAD_RECEIPT_MANIFEST")
    raw = (folder/"W31_CENSUS_REPORT.json").read_bytes()
    need(digest(raw)==receipt["files"]["W31_CENSUS_REPORT.json"],"RECEIPT_DRIFT")
    obj = json.loads(raw)
    need(obj["governance"]["merge_admission"]=="HOLD" and
         obj["scheduler_proposal"]["mutation_enabled"] is False,"REPORT_PROMOTION")
    return receipt


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--head",required=True)
    p.add_argument("--run-id",type=int)
    p.add_argument("--attempt",type=int)
    p.add_argument("--verify-only",action="store_true")
    a=p.parse_args()
    if not a.verify_only:
        write(json.loads(a.input.read_text(encoding="utf-8")), a.out, head=a.head,
              run_id=a.run_id,attempt=a.attempt)
    print(json.dumps(verify(a.out,head=a.head),sort_keys=True))


if __name__ == "__main__":
    main()
