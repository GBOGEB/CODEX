"""Turn one Docker->lldb-server probe receipt into a per-lane LDAB debugger receipt.

The lane receipt carries the fields ABACUS `bd_ldab_join_census.py` expects for a
debugger receipt: repository, source_sha, run_id, job_id, evidence_url,
real_probe_steps, runner_id, session_id, port_lease_id, container_id,
image_digest, host_binding.

Honesty rules: a missing or non-ACCEPT probe yields real_probe_steps=0 and
session_id/port_lease_id=null (never a fabricated id). host_port is read from the
probe's own `docker port` observation, never assigned here. All fields stay
unverified; the joiner checks shape only.

Subcommands: lane | aggregate
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_LANE = "codex.lldb.lane.receipt.v1"
SCHEMA_AGG = "codex.lldb.lane.aggregate.v1"
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
BIND_RE = re.compile(r"^127\.0\.0\.1:(\d{1,5})$")


def _load(path: Path) -> dict | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return data if isinstance(data, dict) else None


def build_lane(probe: dict | None, *, lane: str, source_sha: str, repository: str,
               run_id: str | None, job_id: str | None, runner_id: str | None,
               server_url: str = "https://github.com") -> dict:
    if not SHA_RE.match(source_sha or ""):
        raise ValueError("source_sha must be a full 40-hex commit id")
    accepted = bool(probe) and probe.get("status") == "ACCEPT"
    steps = int(probe.get("real_probe_steps") or 0) if accepted else 0
    container = (probe or {}).get("container_id") if accepted else None
    binding = (probe or {}).get("host_binding") if accepted else None
    match = BIND_RE.match(binding or "")
    live = accepted and steps > 0 and bool(container) and bool(match) and bool(runner_id)
    ident = f"{run_id}-{lane}-{str(container)[:12]}" if live else None
    url = None
    if run_id and job_id:
        url = f"{server_url}/{repository}/actions/runs/{run_id}/job/{job_id}"
    return {
        "schema": SCHEMA_LANE,
        "lane": lane,
        "repository": repository,
        "source_sha": source_sha,
        "run_id": run_id,
        "job_id": job_id,
        "evidence_url": url,
        "runner_id": runner_id,
        "probe_status": (probe or {}).get("status", "MISSING"),
        "real_probe_steps": steps,
        "session_id": ident,
        "port_lease_id": ident,
        "container_id": container,
        "image_digest": (probe or {}).get("image_id") if accepted else None,
        "host_binding": binding if match else None,
        "host_port": int(match.group(1)) if match else None,
        "container_port": 4711,
        "counts_as_authenticated_session": bool(live),
        "authority_transfer": False,
        "formal_credit_delta": 0,
        "engineering_credit_delta": 0,
    }


def aggregate(lanes: list[dict], expected: int | None = None) -> dict:
    sessions = [x for x in lanes if x.get("counts_as_authenticated_session")]
    ids = [x["lane"] for x in lanes]
    out = {
        "schema": SCHEMA_AGG,
        "lanes_reported": len(lanes),
        "lanes_expected": expected,
        "all_lanes_reported": (expected is None or len(set(ids)) == expected)
        and len(ids) == len(set(ids)),
        "authenticated_sessions": len(sessions),
        "total_real_probe_steps": sum(int(x.get("real_probe_steps") or 0) for x in lanes),
        "lanes_not_counted": sorted(
            x["lane"] for x in lanes if not x.get("counts_as_authenticated_session")
        ),
        "source_shas": sorted({x.get("source_sha") for x in lanes}),
    }
    out["single_source_sha"] = len(out["source_shas"]) == 1
    return out


def _write(path: Path, body: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(body, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("lane")
    a.add_argument("--probe", type=Path, required=True)
    a.add_argument("--lane", required=True)
    a.add_argument("--source-sha", required=True)
    a.add_argument("--job-id", default=None)
    a.add_argument("--out", type=Path, required=True)
    b = sub.add_parser("aggregate")
    b.add_argument("--lanes", type=Path, nargs="+", required=True)
    b.add_argument("--expected", type=int, default=None)
    b.add_argument("--out", type=Path, required=True)
    args = ap.parse_args(argv)

    if args.cmd == "lane":
        body = build_lane(
            _load(args.probe),
            lane=args.lane,
            source_sha=args.source_sha,
            repository=os.environ.get("GITHUB_REPOSITORY", "GBOGEB/CODEX"),
            run_id=os.environ.get("GITHUB_RUN_ID"),
            job_id=args.job_id,
            runner_id=os.environ.get("RUNNER_NAME"),
            server_url=os.environ.get("GITHUB_SERVER_URL", "https://github.com"),
        )
        _write(args.out, body)
        print(f"lane {args.lane}: probe={body['probe_status']} steps={body['real_probe_steps']} "
              f"session={'yes' if body['counts_as_authenticated_session'] else 'no'}")
        return 0
    lanes = [x for x in (_load(p) for p in args.lanes) if x]
    body = aggregate(lanes, args.expected)
    _write(args.out, body)
    print(json.dumps(body, indent=2, sort_keys=True))
    ok = body["all_lanes_reported"] and body["single_source_sha"]
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
