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


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    payload = ROOT / manifest["mirrored_path"]
    observed_hash = sha256(payload)
    payload_hash_ok = observed_hash == manifest["source_sha256"]

    swiftc = shutil.which("swiftc")
    lldb = shutil.which("lldb")
    lldb_dap = shutil.which("lldb-dap") or shutil.which("lldb-vscode")
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
        "schema": "codex.qps_federated_lldb_receipt.v1",
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
            "lldb": lldb,
            "lldb_dap": lldb_dap,
        },
        "adapter": {
            "canonical": "lldb-dap",
            "surface_present": bool(lldb_dap),
            "execution_driver": "lldb-cli-batch",
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
