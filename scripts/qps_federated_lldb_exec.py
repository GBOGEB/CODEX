#!/usr/bin/env python3
"""Execute an exact QPS Swift payload on the CODEX macOS runner.

This is a federated escape lane for runtime proof. It does not claim that the
cryoplant repository-local hosted-runner admission gate has recovered.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "runtime/debug/federation/qps_federated_payload_manifest.json"
OUT = ROOT / "artifacts/qps_debug"


def run(args: list[str], timeout: int = 180) -> dict:
    try:
        proc = subprocess.run(
            args,
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        return {
            "cmd": args,
            "returncode": proc.returncode,
            "stdout": proc.stdout[-16000:],
            "stderr": proc.stderr[-16000:],
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "cmd": args,
            "returncode": 124,
            "stdout": exc.stdout or "",
            "stderr": exc.stderr or "timed out",
        }


def resolve_tool(*names: str) -> tuple[str | None, str]:
    for name in names:
        direct = shutil.which(name)
        if direct:
            return direct, "PATH"
    xcrun = shutil.which("xcrun")
    if xcrun:
        for name in names:
            result = run([xcrun, "--find", name], 30)
            candidate = result.get("stdout", "").strip()
            if result.get("returncode") == 0 and candidate:
                return candidate, "XCRUN"
    return None, "NOT_FOUND"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    payload = ROOT / manifest["mirrored_path"]
    observed_hash = sha256(payload)
    payload_hash_ok = observed_hash == manifest["source_sha256"]

    swiftc, swiftc_source = resolve_tool("swiftc")
    lldb, lldb_source = resolve_tool("lldb")
    lldb_dap, lldb_dap_source = resolve_tool("lldb-dap", "lldb-vscode")
    adapter_probe = (
        run([lldb_dap, "--help"], 30)
        if lldb_dap
        else {"returncode": None, "reason": "lldb_dap_not_found"}
    )
    OUT.mkdir(parents=True, exist_ok=True)
    binary = OUT / "qps_federated_probe"

    if not payload_hash_ok:
        compile_result = {"returncode": None, "reason": "payload_hash_mismatch"}
        debug_result = {"returncode": None, "reason": "payload_hash_mismatch"}
        steps = 0
        status = "REJECT"
    elif not swiftc or not lldb:
        compile_result = {"returncode": None, "reason": "swiftc_or_lldb_missing"}
        debug_result = {"returncode": None, "reason": "swiftc_or_lldb_missing"}
        steps = 0
        status = "DEFER"
    else:
        compile_result = run(
            [swiftc, "-g", "-parse-as-library", str(payload), "-o", str(binary)]
        )
        if compile_result["returncode"] != 0:
            debug_result = {"returncode": None, "reason": "compile_failed"}
            steps = 0
            status = "REJECT"
        else:
            debug_result = run(
                [
                    lldb,
                    "--batch",
                    "-o",
                    f"target create {binary}",
                    "-o",
                    "breakpoint set --file Probe.swift --line 4",
                    "-o",
                    "run",
                    "-o",
                    "thread step-over",
                    "-o",
                    "thread step-over",
                    "-o",
                    "thread backtrace",
                ]
            )
            combined = (
                f"{debug_result.get('stdout', '')}\n"
                f"{debug_result.get('stderr', '')}"
            )
            steps = (
                combined.count("stop reason")
                + combined.count("frame #")
                + combined.count("thread step-over")
            )
            observed_42 = "observed=42" in combined
            status = (
                "ACCEPT"
                if debug_result["returncode"] == 0 and steps > 0 and observed_42
                else "REJECT"
            )

    receipt = {
        "schema": "codex.qps_federated_lldb_receipt.v2",
        "receipt_id": "CODEX-QPS-FEDERATED-LLDB-001",
        "created_utc": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "classification": "MAINTENANCE_RUNTIME_ONLY",
        "source": {
            "repository": manifest["source_repository"],
            "exact_sha": manifest["source_exact_sha"],
            "path": manifest["source_path"],
            "git_blob_sha": manifest["source_git_blob_sha"],
            "expected_sha256": manifest["source_sha256"],
            "observed_sha256": observed_hash,
            "payload_hash_match": payload_hash_ok,
        },
        "executor": {
            "repository": os.getenv("GITHUB_REPOSITORY", "GBOGEB/CODEX"),
            "exact_sha": os.getenv("GITHUB_SHA", "UNKNOWN"),
            "runner_name": os.getenv("RUNNER_NAME"),
            "runner_os": os.getenv("RUNNER_OS"),
            "runner_arch": os.getenv("RUNNER_ARCH"),
            "swiftc": swiftc,
            "swiftc_resolution": swiftc_source,
            "lldb": lldb,
            "lldb_resolution": lldb_source,
            "lldb_dap": lldb_dap,
            "lldb_dap_resolution": lldb_dap_source,
        },
        "adapter": {
            "canonical": "lldb-dap",
            "surface_present": bool(lldb_dap),
            "surface_probe_returncode": adapter_probe.get("returncode"),
            "surface_state": "READY" if lldb_dap else "DEFER_NOT_FOUND",
            "execution_driver": "lldb-cli-batch",
            "execution_backend": "LLDB",
        },
        "probe_status": status,
        "dov_status": "PASS" if status == "ACCEPT" else "WITHHELD",
        "real_probe_steps": steps,
        "minimum_victory_condition": {
            "exact_qps_payload_hash_match": payload_hash_ok,
            "swift_compile_returncode_zero": compile_result.get("returncode") == 0,
            "lldb_returncode_zero": debug_result.get("returncode") == 0,
            "real_probe_steps_gt_zero": steps > 0,
            "observed_value_42": (
                "observed=42"
                in (
                    f"{debug_result.get('stdout', '')}\n"
                    f"{debug_result.get('stderr', '')}"
                )
            ),
        },
        "compile": compile_result,
        "lldb": debug_result,
        "adapter_probe": adapter_probe,
        "authority_guards": {
            "qps_repo_local_runner_gate": "WITHHELD_EXTERNAL",
            "federated_execution_does_not_claim_repo_local_runner_recovery": True,
            "formal_engineering_credit_delta": 0,
            "negotiation_credit_delta": 0,
        },
    }
    receipt["receipt_sha256"] = hashlib.sha256(
        json.dumps(receipt, sort_keys=True).encode()
    ).hexdigest()
    target = OUT / "qps_federated_lldb_receipt.json"
    target.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if status == "ACCEPT" else (3 if status == "DEFER" else 2)


if __name__ == "__main__":
    raise SystemExit(main())
