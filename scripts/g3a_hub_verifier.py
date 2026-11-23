#!/usr/bin/env python3
"""G3A Hub-scope readback verifier (read-only, receipt based).

The ABACUS G3A runner only verifies local files for GBOGEB/ABACUS. The Hub
JADE gates (run conclusion at an exact SHA, open review threads, independent
approval, required contexts) need GitHub readbacks. This tool never calls
GitHub. It judges a pinned JSON *readback receipt* and returns, per gate,
PASS / FAIL / UNKNOWN. It grants no approval, merge, waiver or dispatch.

Usage::

    python scripts/g3a_hub_verifier.py RECEIPT.json

Exit 0: every gate PASS. Exit 1: some gate FAIL. Exit 2: not eligible
(bad schema/SHA or UNKNOWN evidence). Exit 3: unreadable input.

Rules (non-compensating):
* A check passes only on exact-head evidence: the run's ``head_sha`` must equal
  the pull request head, and that head must equal ``expected_head_sha``.
* Missing, null, truncated-SHA or non-terminal evidence is UNKNOWN, never PASS.
* A gate with zero checks is FAIL (an empty set is not a pass).
* For a run name at one SHA, any completed FAILURE/CANCELLED/TIMED_OUT/
  ACTION_REQUIRED run fails the check even if another run of the same name
  succeeded (no RED hidden behind a later green). Queued/skipped is not success.
* Gates are sequential: a gate is only credited when every earlier gate passed.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

SCHEMA = "g3a.hub-readback.v1"
HEAD = re.compile(r"[0-9a-f]{40}\Z")
BAD_CONCLUSIONS = {"failure", "cancelled", "timed_out", "action_required", "startup_failure"}
KINDS = {"run_success", "threads_zero", "approvals_min", "contexts_success"}
GATE_IDS = ("A1", "A2", "A3")
PASS, FAIL, UNKNOWN = "PASS", "FAIL", "UNKNOWN"


class Ineligible(ValueError):
    """Receipt cannot be judged (schema or SHA problem)."""


def _is_head(value) -> bool:
    return isinstance(value, str) and HEAD.fullmatch(value) is not None


def validate(rec: dict) -> None:
    if not isinstance(rec, dict) or rec.get("schema") != SCHEMA:
        raise Ineligible("unknown receipt schema")
    if rec.get("repository") != "GBOGEB/pipeline-automation-hub":
        raise Ineligible("unsupported repository")
    if not isinstance(rec.get("mission_id"), str) or not re.fullmatch(r"[A-Za-z0-9_.-]{1,80}", rec["mission_id"]):
        raise Ineligible("invalid mission id")
    if type(rec.get("start_index")) is not int or rec["start_index"] < 0:
        raise Ineligible("invalid start_index")
    if not isinstance(rec.get("index_namespace"), str) or not rec["index_namespace"].strip():
        raise Ineligible("index_namespace required (do not reuse the ABACUS g3a_n index)")
    if not _is_head(rec.get("expected_head_sha")):
        raise Ineligible("expected_head_sha must be a full 40-char SHA")
    gates = rec.get("gates")
    if not isinstance(gates, list) or [g.get("id") if isinstance(g, dict) else None for g in gates] != list(GATE_IDS):
        raise Ineligible("gates must be exactly A1, A2, A3 in order")
    for key in ("pulls", "runs"):
        if not isinstance(rec.get(key), list):
            raise Ineligible(f"{key} must be a list")


def _pull(rec: dict, number):
    found = [p for p in rec["pulls"] if isinstance(p, dict) and p.get("number") == number]
    return found[0] if len(found) == 1 else None


def _head_state(rec: dict, pr: dict | None) -> str | None:
    """Return None when the PR head is exact, else FAIL/UNKNOWN."""
    if pr is None or not _is_head(pr.get("head_sha")):
        return UNKNOWN
    return None if pr["head_sha"] == rec["expected_head_sha"] else FAIL


def judge_check(rec: dict, chk: dict) -> tuple[str, str]:
    kind = chk.get("kind") if isinstance(chk, dict) else None
    if kind not in KINDS:
        return UNKNOWN, "unapproved check kind"
    pr = _pull(rec, chk.get("pr"))
    stale = _head_state(rec, pr)
    if stale == UNKNOWN:
        return UNKNOWN, "pull request or its head SHA missing/truncated"
    if stale == FAIL:
        return FAIL, "pull request head differs from expected head"
    if kind == "threads_zero":
        n = pr.get("unresolved_threads")
        if type(n) is not int or n < 0:
            return UNKNOWN, "unresolved thread count unknown"
        return (PASS, "0 unresolved threads") if n == 0 else (FAIL, f"{n} unresolved threads")
    if kind == "approvals_min":
        n, need = pr.get("independent_approvals"), chk.get("minimum")
        if type(n) is not int or type(need) is not int or need < 1:
            return UNKNOWN, "approval count or minimum unknown"
        return (PASS, f"{n} independent approvals") if n >= need else (FAIL, f"{n} < {need} approvals")
    names = [chk.get("name")] if kind == "run_success" else chk.get("names")
    if not isinstance(names, list) and kind == "contexts_success":
        return UNKNOWN, "names must be a list"
    names = [n for n in names] if isinstance(names, list) else []
    if not names or not all(isinstance(n, str) and n for n in names):
        return FAIL, "empty or invalid run-name set"
    worst, detail = PASS, "all named runs succeeded at exact head"
    for name in names:
        runs = [r for r in rec["runs"] if isinstance(r, dict) and r.get("name") == name
                and r.get("head_sha") == pr["head_sha"]]
        if not runs:
            return UNKNOWN, f"no run named {name!r} at the exact head"
        # keep only the latest attempt per run_id
        latest = {}
        for r in runs:
            key = r.get("run_id")
            if key not in latest or (type(r.get("attempt")) is int and r["attempt"] > latest[key].get("attempt", -1)):
                latest[key] = r
        for r in latest.values():
            if r.get("status") != "completed":
                worst, detail = UNKNOWN, f"{name!r} run {r.get('run_id')} not completed"
                continue
            concl = r.get("conclusion")
            if concl in BAD_CONCLUSIONS:
                return FAIL, f"{name!r} run {r.get('run_id')} concluded {concl}"
            if concl != "success" and worst == PASS:
                worst, detail = UNKNOWN, f"{name!r} run {r.get('run_id')} conclusion {concl!r} is not success"
    return worst, detail


def judge(rec: dict) -> dict:
    validate(rec)
    results, blocked = [], False
    accepted = 0
    for gate in rec["gates"]:
        checks = gate.get("checks")
        if not isinstance(checks, list) or not checks:
            verdict, rows = FAIL, [{"verdict": FAIL, "detail": "gate has zero checks"}]
        else:
            rows = []
            for chk in checks:
                v, d = judge_check(rec, chk)
                rows.append({"verdict": v, "detail": d})
            vs = {r["verdict"] for r in rows}
            verdict = FAIL if FAIL in vs else UNKNOWN if UNKNOWN in vs else PASS
        credited = verdict == PASS and not blocked
        if credited:
            accepted += 1
        if verdict != PASS:
            blocked = True
        results.append({"id": gate["id"], "verdict": verdict, "credited": credited, "checks": rows})
    return {"mission_id": rec["mission_id"], "index_namespace": rec["index_namespace"],
            "start_index": rec["start_index"], "actual_index": rec["start_index"] + accepted,
            "accepted_checkpoints": accepted, "gates": results,
            "boundary": "readback judgement only; no approval, merge, waiver or dispatch"}


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: g3a_hub_verifier.py RECEIPT.json")
        return 3
    try:
        rec = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
        out = judge(rec)
    except Ineligible as exc:
        print(f"INELIGIBLE: {exc}")
        return 2
    except (OSError, ValueError) as exc:
        print(f"UNREADABLE: {exc}")
        return 3
    print(json.dumps(out, indent=2, sort_keys=True))
    verdicts = [g["verdict"] for g in out["gates"]]
    return 0 if all(v == PASS for v in verdicts) else 1 if FAIL in verdicts else 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
