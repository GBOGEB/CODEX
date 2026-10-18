#!/usr/bin/env python3
"""CODE PURPLE Swift roof: read-only source census and native-proof boundary.

CODEX owns this projection, not QPS engineering facts, ABACUS root closures,
GitHub rules, dispatcher authority, or the historical KEB receipt registry.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
from datetime import UTC, datetime
from pathlib import Path

SCHEMA = "codepurple.swift.roof.v1"
SHA = re.compile(r"[0-9a-f]{40}\Z")
CODEX = "GBOGEB/CODEX"
QPS = "GBOGEB/cryoplant-project"
ASSETS = (
    (CODEX, "abacus_runtime/debug_spine/swift/Package.swift", "PACKAGE_MANIFEST"),
    (CODEX, "abacus_runtime/debug_spine/swift/Sources/AbacusDebugSpine/main.swift", "SWIFT_DAP_BACKBONE"),
    (CODEX, "runtime/debug/federation/qps_payload/Probe.swift", "PINNED_QPS_MIRROR"),
    (CODEX, "runtime/debug/lldb_dap_probe/Probe.swift", "CODEX_NATIVE_PROBE"),
    (QPS, "triage/runtime_health/lldb_probe/Probe.swift", "QPS_CHILD_NATIVE_SOURCE"),
)
QPS_SNAPSHOT = "c07666b2dfc77f97980e8661fac3864f975e2d76"
BAD_FOLDERS = frozenset({".git", ".build", ".swiftpm", "node_modules", ".venv", "__pycache__"})


def demand(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError("SWIFT_ROOF_HOLD:" + message)


def digest(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def checked_head(root: Path, expected_sha: str | None = None) -> str:
    p = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, text=True,
                       capture_output=True, check=False, timeout=15)
    sha = p.stdout.strip()
    demand(p.returncode == 0 and SHA.fullmatch(sha) is not None, "unknown git source HEAD")
    if expected_sha:
        demand(SHA.fullmatch(expected_sha) is not None and sha == expected_sha,
               "checked-out head differs from requested exact head")
    return sha


def source_census(root: Path, source_sha: str) -> dict:
    demand(SHA.fullmatch(source_sha) is not None, "invalid source sha")
    want = {p for r, p, _ in ASSETS if r == CODEX}
    found = {
        p.relative_to(root).as_posix() for p in root.rglob("*.swift")
        if p.is_file() and not (BAD_FOLDERS & set(p.relative_to(root).parts))
    }
    missing = sorted(want - found)
    unregistered = sorted(found - want)
    rows = []
    for repo, path, role in ASSETS:
        local = repo == CODEX
        p = root / path
        rows.append({
            "repository": repo, "path": path, "role": role,
            "source_sha": source_sha if local else QPS_SNAPSHOT,
            "content_sha256": hashlib.sha256(p.read_bytes()).hexdigest() if local and p.is_file() else None,
            "binding": "LOCAL_BYTES_HASHED" if local and p.is_file() else "EXTERNAL_DECLARED_NOT_READBACK",
            "authority": "CODEX_SOURCE" if local else "QPS_CHILD_SOURCE",
        })
    return {
        "source_sha": source_sha,
        "assets": rows,
        "eligible_local": len(found), "registered_local": len(want & found),
        "eligible_federated_declared": len(ASSETS),
        "federated_verified": None,
        "local_missing": missing, "local_unregistered": unregistered,
        "local_mapping_complete": not (missing or unregistered),
        "qps_source_freshness": "UNKNOWN_UNTIL_QPS_EXACT_HEAD_READBACK",
    }


def native_stops(output: str) -> dict:
    """Count LLDB-completed commands only; never echoed commands or backtraces.

    An actual stop must occur inside the corresponding LLDB command section.
    The later `thread backtrace` can repeat the last stop reason, so an
    unscoped `output.count("stop reason = step over")` is not sufficient.
    """
    sections = re.split(r"\(lldb\)\s+", output)
    breakpoint_stops = 0
    step_stops = 0
    backtrace = False
    for section in sections:
        cmd = section.strip().split("\n", 1)[0].strip()
        if cmd == "run" and re.search(r"Process\s+\d+\s+stopped.*?stop reason\s*=\s*breakpoint", section, re.I | re.S):
            breakpoint_stops += 1
        if cmd == "thread step-over" and re.search(r"Process\s+\d+\s+stopped.*?stop reason\s*=\s*step over\b", section, re.I | re.S):
            step_stops += 1
        if cmd == "thread backtrace" and re.search(r"\bframe\s*#\s*0\s*:", section):
            backtrace = True
    return {"breakpoint_stops": breakpoint_stops, "step_stops": step_stops,
            "backtrace_present": backtrace}


def verify_native(receipt: dict, source_sha: str) -> dict:
    demand(SHA.fullmatch(source_sha) is not None, "invalid verification SHA")
    demand(receipt.get("repo") == CODEX and receipt.get("exact_head_sha") == source_sha,
           "foreign or stale native receipt")
    claimed = receipt.get("receipt_sha256")
    proof = dict(receipt)
    proof.pop("receipt_sha256", None)
    # Existing CODEX producer hashes json.dumps(sort_keys=True) with default separators.
    calculated = hashlib.sha256(json.dumps(proof, sort_keys=True).encode()).hexdigest()
    demand(type(claimed) is str and claimed == calculated, "native receipt SHA256 mismatch")
    run = receipt.get("probe") or {}
    events = native_stops((run.get("lldb") or {}).get("stdout", ""))
    demand(receipt.get("probe_status") == "ACCEPT" and receipt.get("dov_status") == "PASS",
           "native receipt is not accepted")
    demand(run.get("status") == "ACCEPT" and (run.get("lldb") or {}).get("returncode") == 0,
           "LLDB subprocess not clean")
    demand(events["breakpoint_stops"] >= 1 and events["step_stops"] >= 2
           and events["backtrace_present"], "no genuine LLDB breakpoint, two step stops and backtrace")
    demand(run.get("steps") == events["step_stops"], "step counter is command/trace inflated")
    demand(receipt.get("minimum_victory_condition", {}).get("real_probe_steps_gt_zero") is True,
           "missing minimum-victory condition")
    return {
        "source_sha": source_sha, "native_cli_probe": "PASS",
        "native_cli_steps": events["step_stops"], "breakpoints": events["breakpoint_stops"],
        "lldb_dap_live": "UNVERIFIED", "docker_native": "UNVERIFIED",
        "mcp_native": "UNVERIFIED", "qps_current_head_accepted": "UNVERIFIED",
        "native_job_id": None, "native_job_first_page": "NOT_COLLECTED",
        "credit": 0, "admission": "HOLD",
    }


def graph() -> dict:
    nodes = [
        ("SOURCE", 0, "CODEX and QPS source", "SOURCE"),
        ("CENSUS", 1, "Five Swift assets", "INVENTORY"),
        ("FORWARD", 2, "Version and runner preflight", "PLANNING"),
        ("LINUX", 3, "Ubuntu census and negative tests", "TEST"),
        ("MACOS", 3, "macOS native LLDB CLI", "TEST"),
        ("DOCKER", 3, "QPS conditional Docker lane", "EXTERNAL_OWNER"),
        ("MCP", 3, "CODEX strict MCP lane", "EXTERNAL_OWNER"),
        ("KEB", 4, "CODEX native KEB receipt", "EVIDENCE"),
        ("LDAB", 5, "ABACUS LDAB/LLDB debug join", "ANALYSIS"),
        ("DOW", 6, "ABACUS DOW disposition", "CONSUMER"),
        ("QPS", 7, "QPS TRIAGE owner re-entry", "CHILD"),
        ("NEXT", 8, "MIP next pulse", "FEEDBACK"),
    ]
    ed = [
        ("SOURCE", "CENSUS"), ("CENSUS", "FORWARD"),
        ("FORWARD", "LINUX"), ("FORWARD", "MACOS"),
        ("FORWARD", "DOCKER"), ("FORWARD", "MCP"),
        ("LINUX", "KEB"), ("MACOS", "KEB"),
        ("KEB", "LDAB"), ("LDAB", "DOW"), ("DOW", "QPS"), ("QPS", "NEXT"),
    ]
    rank = {n: r for n, r, _, _ in nodes}
    demand(all(rank[a] < rank[b] for a, b in ed), "cyclic forward DAG")
    return {"nodes": [{"id": n, "rank": r, "label": t, "kind": k} for n, r, t, k in nodes],
            "edges": [{"from": a, "to": b, "kind": "DECLARED_FEEDFORWARD"} for a, b in ed],
            "next_pulse_edges": [{"from": "NEXT", "to": "SOURCE", "kind": "NEXT_PULSE_ONLY"}]}


def sipoc() -> list[dict]:
    return [
        {"id": "S1", "supplier": "CODEX/QPS source owners", "input": "Pinned 40-digit SHAs, tracked Swift paths", "process": "Modernize: discover all code and missing edges", "output": "Five-asset source census", "customer": "CODEX roof preflight"},
        {"id": "S2", "supplier": "CODEX native workflow", "input": "Source SHA, macOS and Ubuntu runner profiles", "process": "Innovate: run negative/preflight and native debugger", "output": "Native CI steps, LLDB stop proof", "customer": "CODEX KEB"},
        {"id": "S3", "supplier": "GitHub Actions", "input": "run, attempt, job ID, artifact SHA256", "process": "Validate provenance and completeness", "output": "Typed native receipt or HOLD", "customer": "ABACUS / LDAB"},
        {"id": "S4", "supplier": "ABACUS DOW and LDAB", "input": "Immutable CODEX artifact and first-red", "process": "Differentiate manifestations and causal roots", "output": "DOW findings, no automatic closure", "customer": "QPS TRIAGE"},
        {"id": "S5", "supplier": "QPS child owner", "input": "CODEX DOW evidence and QPS native runtime", "process": "Child ACCEPT/REJECT/DEFER", "output": "Repo-local child disposition", "customer": "Mission Control read-only census"},
        {"id": "S6", "supplier": "MIP and Mission Control", "input": "Comparable N, N+1 native snapshots", "process": "Perpetuate: detect regressions and next-pulse feedback", "output": "Scoped 3-pulse planned work; no admission promotion", "customer": "Next owner wave"},
    ]


def mermaid(g: dict) -> str:
    s = ["flowchart LR"]
    s += [f'  {n["id"]}["{n["label"]}"]' for n in g["nodes"]]
    s += [f'  {e["from"]} --> {e["to"]}' for e in g["edges"]]
    s += [f'  {e["from"]} -. "N+1 only" .-> {e["to"]}' for e in g["next_pulse_edges"]]
    return "\n".join(s) + "\n"


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--mode", choices=("census", "verify"), default="census")
    p.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--expected-head", default=os.getenv("EXACT_HEAD_SHA"))
    p.add_argument("--receipt", type=Path)
    a = p.parse_args()
    head = checked_head(a.root, a.expected_head)
    census = source_census(a.root, head)
    demand(census["local_mapping_complete"], "unregistered or missing local Swift sources")
    native = None
    if a.mode == "verify":
        demand(a.receipt is not None and a.receipt.is_file(), "native receipt missing")
        native = verify_native(json.loads(a.receipt.read_text()), head)
    g = graph()
    out = {
        "schema": SCHEMA, "observed_at_utc": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "wave": "W1_SWIFT_ROOF", "pulse": "P1_CENSUS" if a.mode == "census" else "P2_NATIVE_RECONCILE",
        "mip": ["MODERNIZE", "INNOVATE", "PERPETUATE"],
        "three_pulse_method": ["P1_DISCOVER_AND_NEGATIVE", "P2_NATIVE_AND_RECEIPT", "P3_FEDERATION_AND_RECURSION"],
        "authority_transfer": False, "dispatch_authorized": False,
        "qps_engineering_credit": 0, "formal_root_closure_credit": 0, "merge_admission": "HOLD",
        "source": census, "graph": g, "sipoc": sipoc(),
        "native": native, "run_id": os.getenv("GITHUB_RUN_ID"),
        "run_attempt": os.getenv("GITHUB_RUN_ATTEMPT"),
        "job_symbol": os.getenv("GITHUB_JOB"), "job_id": None,
        "next_pulse": "P3_QPS_REENTRY_PENDING_OWNER_RECEIPT",
    }
    a.out.mkdir(parents=True, exist_ok=True)
    (a.out / "swift-roof.json").write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    (a.out / "swift-roof.mmd").write_text(mermaid(g))
    hdr = "| Process | Supplier | Input | Transformation | Output | Customer |\n|---|---|---|---|---|---|\n"
    rows = "".join("| " + " | ".join(x[k] for k in ("id", "supplier", "input", "process", "output", "customer")) + " |\n" for x in sipoc())
    (a.out / "swift-roof-sipoc.md").write_text("# SWIFT roof SIPOC (projection only)\n\n" + hdr + rows)
    hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(a.out.iterdir()) if p.is_file()}
    (a.out / "manifest.json").write_text(json.dumps({"schema":"codepurple.swift.roof.hash.v1", "source_sha":head, "sha256":hashes, "admission":"HOLD"},indent=2,sort_keys=True)+"\n")
    print(json.dumps({"result": "PASS" if native or a.mode == "census" else "HOLD", "source_sha": head,
                      "local_registered": census["registered_local"], "local_eligible": census["eligible_local"],
                      "remote_verified": None, "mode": a.mode, "native": native,
                      "merge_admission": "HOLD"}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())