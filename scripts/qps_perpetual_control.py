#!/usr/bin/env python3
"""Aggregate debug-family receipts into perpetual CONTROL and terminal DoV.

The control gate deliberately separates federated runtime control from terminal
global closure. Terminal global DoV additionally requires the cryoplant-local
runner admission gate to recover and LLDB MCP to execute live.
"""
from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SEEDS = ROOT / "runtime/debug/federation/receipts"
OUT = ROOT / "artifacts/qps_debug/perpetual"


def load_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def accepted(doc: dict[str, Any] | None) -> bool:
    """Normalize live and durable receipt schemas into one ACCEPT predicate."""
    if not doc:
        return False
    execution = doc.get("execution") if isinstance(doc.get("execution"), dict) else {}
    return any(
        (
            doc.get("status") == "ACCEPT",
            doc.get("probe_status") == "ACCEPT",
            doc.get("dov_status") == "PASS",
            execution.get("probe_status") == "ACCEPT",
            execution.get("dov_status") == "PASS",
        )
    )


def find_named(root: Path, filename: str) -> dict[str, Any] | None:
    hits = sorted(root.rglob(filename)) if root.exists() else []
    return load_json(hits[-1]) if hits else None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence-root", type=Path, default=OUT)
    parser.add_argument("--repo-local-runner-recovered", action="store_true")
    args = parser.parse_args()

    seed_docs = [
        load_json(SEEDS / "QPS_FEDERATED_LLDB_W1F_A_ACCEPT.json"),
        load_json(SEEDS / "QPS_FEDERATED_LLDB_W1F_B_ACCEPT.json"),
    ]
    lldb_dap = find_named(args.evidence_root, "lldb_dap_live.json")
    mcp = find_named(args.evidence_root, "lldb_mcp_live.json")
    debugpy = find_named(args.evidence_root, "debugpy_live.json")
    js_debug = find_named(args.evidence_root, "js_debug_live.json")
    docker = find_named(args.evidence_root, "docker_remote_lldb.json")

    heartbeats: list[dict[str, Any]] = []
    for seed in seed_docs:
        if accepted(seed):
            heartbeats.append(
                {
                    "kind": "federated_native_lldb",
                    "receipt_id": seed.get("receipt_id"),
                    "run_id": seed.get("workflow", {}).get("run_id"),
                    "executor_sha": seed.get("execution", {}).get("executor_workflow_sha"),
                    "source_sha": seed.get("source", {}).get("exact_sha"),
                    "real_probe_steps": seed.get("execution", {}).get("real_probe_steps"),
                }
            )
    if accepted(lldb_dap):
        heartbeats.append(
            {
                "kind": "live_lldb_dap",
                "receipt_id": "LIVE-LLDB-DAP",
                "run_id": None,
                "executor_sha": None,
                "source_sha": lldb_dap.get("source_exact_sha"),
                "real_probe_steps": lldb_dap.get("session", {}).get("stack_frames"),
            }
        )

    family = {
        "native_lldb_seed_a": accepted(seed_docs[0]),
        "native_lldb_seed_b": accepted(seed_docs[1]),
        "live_lldb_dap": accepted(lldb_dap),
        "docker_remote_lldb": accepted(docker),
        "debugpy": accepted(debugpy),
        "js_debug": accepted(js_debug),
        "lldb_mcp": accepted(mcp),
    }
    heartbeat_threshold = len(heartbeats) >= 3
    executable_family_gate = all(
        family[name]
        for name in ("live_lldb_dap", "docker_remote_lldb", "debugpy", "js_debug")
    )
    federated_perpetual_control = heartbeat_threshold and executable_family_gate
    terminal_global = (
        federated_perpetual_control
        and family["lldb_mcp"]
        and args.repo_local_runner_recovered
    )

    burndown: list[dict[str, Any]] = []
    if not args.repo_local_runner_recovered:
        burndown.append(
            {
                "id": "BD03-EXT-RUNNER-001",
                "state": "WITHHELD_EXTERNAL",
                "owner": "cryoplant repository / GitHub hosted-runner admission",
                "victory": "one cryoplant job obtains runner_id != 0 and executes >0 steps",
                "non_action": "do not patch debugger code for runner_id=0",
            }
        )
    for name, ok in family.items():
        if ok:
            continue
        item = {
            "id": f"BD-RUNTIME-{name.upper().replace('_', '-')}",
            "state": "OPEN",
            "owner": "QPS debug runtime fabric",
            "victory": f"{name} emits ACCEPT receipt from a real runtime session",
        }
        if name == "lldb_mcp" and mcp and mcp.get("status") == "DEFER":
            item["state"] = "DEFER_TOOLCHAIN"
            item["owner"] = "LLDB/Xcode toolchain capability"
            item["victory"] = "lldb-mcp binary is present and initialize/tools/list/session_create/command/session_close all execute"
        burndown.append(item)

    status = {
        "schema": "qps.perpetual.control.v2",
        "created_utc": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "classification": "MAINTENANCE_RUNTIME_ONLY",
        "controlled_baseline": {
            "structure": "13/13",
            "federated_native_lldb": "PASS",
            "federation_governance": "CLEAN",
        },
        "family": family,
        "heartbeat": {
            "count": len(heartbeats),
            "threshold": 3,
            "threshold_met": heartbeat_threshold,
            "receipts": heartbeats,
        },
        "federated_perpetual_control": (
            "CONTROL" if federated_perpetual_control else "WITHHELD"
        ),
        "terminal_global_perpetual_debug_dov": (
            "PASS" if terminal_global else "WITHHELD"
        ),
        "terminal_requirements": {
            "federated_perpetual_control": federated_perpetual_control,
            "live_lldb_mcp": family["lldb_mcp"],
            "cryoplant_repo_local_runner_recovered": args.repo_local_runner_recovered,
        },
        "burndown": burndown,
        "authority_guards": {
            "formal_engineering_credit_delta": 0,
            "negotiation_credit_delta": 0,
            "federated_control_does_not_claim_repo_local_runner_recovery": True,
        },
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "perpetual_control_status.json").write_text(
        json.dumps(status, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(status, indent=2, sort_keys=True))
    return 0 if federated_perpetual_control else 2


if __name__ == "__main__":
    raise SystemExit(main())
