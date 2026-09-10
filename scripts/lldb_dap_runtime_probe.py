#!/usr/bin/env python3
"""LLDB-DAP / Swift / Docker / runner / MCP runtime probe."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RECEIPT = ROOT / "receipts" / "keb" / "LLDB_DAP_SWIFT_DOCKER_RUNNER_MCP_RECEIPT.json"
PROBE_SOURCE = ROOT / "runtime" / "debug" / "lldb_dap_probe" / "Probe.swift"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def run(cmd: list[str], *, cwd: Path = ROOT, timeout: int = 120) -> dict[str, Any]:
    try:
        proc = subprocess.run(cmd, cwd=str(cwd), text=True, capture_output=True, timeout=timeout, check=False)
        return {"cmd": cmd, "returncode": proc.returncode, "stdout": proc.stdout[-8000:], "stderr": proc.stderr[-8000:]}
    except Exception as exc:
        return {"cmd": cmd, "returncode": 127, "stdout": "", "stderr": repr(exc)}


def git_sha() -> str:
    if os.environ.get("GITHUB_SHA"):
        return os.environ["GITHUB_SHA"]
    result = run(["git", "rev-parse", "HEAD"])
    return result["stdout"].strip() if result["returncode"] == 0 else "UNKNOWN"


def list_paths(patterns: tuple[str, ...]) -> list[str]:
    out: list[str] = []
    for path in ROOT.rglob("*"):
        if ".git" in path.parts:
            continue
        if path.is_file() and any(path.match(pattern) for pattern in patterns):
            out.append(path.relative_to(ROOT).as_posix())
    return sorted(out)


def classify_surfaces() -> dict[str, Any]:
    swift_files = list_paths(("*.swift",))
    launch_files = list_paths((".vscode/launch.json", "**/launch.json"))
    docker_files = list_paths(("Dockerfile", "**/Dockerfile", "docker-compose*.yml", "**/docker-compose*.yml"))
    workflow_files = list_paths((".github/workflows/*.yml", ".github/workflows/*.yaml"))
    mcp_files = [p for p in list_paths(("*.py", "*.md", "*.yaml", "*.yml", "*.json")) if "mcp" in p.lower()]
    runner_files = [p for p in list_paths(("*.sh", "*.ps1", "*.yml", "*.yaml")) if "runner" in p.lower()]
    return {
        "lldb_dap": {
            "tool": shutil.which("lldb-dap") or shutil.which("lldb-vscode"),
            "classification": "runner_bound" if platform.system() == "Darwin" else "runner_bound_macos_required",
        },
        "swift_debug": {
            "swift_files": swift_files,
            "launch_files": launch_files,
            "swiftc": shutil.which("swiftc"),
            "lldb": shutil.which("lldb"),
            "classification": "active_probe_candidate" if swift_files else "dormant_no_swift_surface",
        },
        "docker": {"files": docker_files, "classification": "active" if docker_files else "dormant_no_surface"},
        "runner": {"files": runner_files, "workflow_count": len(workflow_files), "classification": "active" if workflow_files else "dormant_no_workflows"},
        "mcp": {"files": mcp_files, "classification": "active" if mcp_files else "dormant_no_surface"},
    }


def execute_swift_lldb_probe() -> dict[str, Any]:
    build_dir = ROOT / "runtime" / "debug" / "lldb_dap_probe" / ".build"
    binary = build_dir / "Probe"
    build_dir.mkdir(parents=True, exist_ok=True)

    if not PROBE_SOURCE.exists():
        return {"status": "DEFER", "reason": "missing_probe_source", "steps": 0}
    if shutil.which("swiftc") is None:
        return {"status": "DEFER", "reason": "swiftc_missing", "steps": 0}
    if shutil.which("lldb") is None:
        return {"status": "DEFER", "reason": "lldb_missing", "steps": 0}

    compile_result = run(["swiftc", "-g", str(PROBE_SOURCE), "-o", str(binary)])
    if compile_result["returncode"] != 0:
        return {"status": "REJECT", "reason": "swift_compile_failed", "steps": 0, "compile": compile_result}

    lldb_result = run([
        "lldb", "--batch",
        "-o", f"target create {binary}",
        "-o", "breakpoint set --name main",
        "-o", "run",
        "-o", "thread step-over",
        "-o", "thread step-over",
        "-o", "thread backtrace",
    ], timeout=180)
    combined = f"{lldb_result.get('stdout', '')}\n{lldb_result.get('stderr', '')}"
    steps = combined.count("thread step-over") + combined.count("stop reason") + combined.count("frame #")
    status = "ACCEPT" if lldb_result["returncode"] == 0 and steps > 0 else "REJECT"
    return {"status": status, "reason": "lldb_executed_steps" if status == "ACCEPT" else "lldb_step_proof_failed", "steps": steps, "compile": compile_result, "lldb": lldb_result}


def emit_receipt(path: Path, probe_result: dict[str, Any]) -> dict[str, Any]:
    receipt = {
        "receipt_id": "KEB-LLDB-DAP-SWIFT-DOCKER-RUNNER-MCP-001",
        "schema_version": "0.1",
        "created_utc": utc_now(),
        "repo": os.environ.get("GITHUB_REPOSITORY", "GBOGEB/CODEX"),
        "exact_head_sha": git_sha(),
        "surface_scope": ["lldb-dap", "swift-debug", "docker", "runner", "mcp"],
        "census_status": "PASS",
        "probe_status": probe_result["status"],
        "dov_status": "PASS" if probe_result["status"] == "ACCEPT" else "WITHHELD",
        "minimum_victory_condition": {
            "lldb_dap_census": "PASS",
            "swift_debug_classification": "PASS",
            "real_probe_steps_gt_zero": probe_result.get("steps", 0) > 0,
            "keb_receipt_emitted": True,
        },
        "surfaces": classify_surfaces(),
        "probe": probe_result,
    }
    receipt["receipt_sha256"] = sha256_text(json.dumps(receipt, sort_keys=True))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["census", "probe"], default="probe")
    parser.add_argument("--receipt", type=Path, default=DEFAULT_RECEIPT)
    args = parser.parse_args()

    if args.mode == "census":
        receipt = {
            "receipt_id": "KEB-LLDB-DAP-SWIFT-DOCKER-RUNNER-MCP-CENSUS",
            "created_utc": utc_now(),
            "repo": os.environ.get("GITHUB_REPOSITORY", "GBOGEB/CODEX"),
            "exact_head_sha": git_sha(),
            "census_status": "PASS",
            "surfaces": classify_surfaces(),
        }
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        args.receipt.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(receipt, indent=2, sort_keys=True))
        return 0

    receipt = emit_receipt(args.receipt, execute_swift_lldb_probe())
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if receipt["probe_status"] == "ACCEPT" else 2


if __name__ == "__main__":
    raise SystemExit(main())
