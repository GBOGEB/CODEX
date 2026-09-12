#!/usr/bin/env python3
"""Run one real Node DAP session through the pinned vscode-js-debug server."""
from __future__ import annotations

import argparse
import json
import os
import socket
import subprocess
import tempfile
import threading
import time
from pathlib import Path
from typing import Any

from qps_debug_protocol_probe import execute_dap_session, write_receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--server-path", required=True)
    args = parser.parse_args()

    target_dir = Path(tempfile.mkdtemp(prefix="qps-js-debug-"))
    target = target_dir / "probe.js"
    target.write_text(
        "const seed=41; const observed=seed+1; console.log(`observed=${observed}`);\n",
        encoding="utf-8",
    )

    candidate = socket.socket()
    candidate.bind(("127.0.0.1", 0))
    port = candidate.getsockname()[1]
    candidate.close()

    server = subprocess.Popen(
        ["node", args.server_path, str(port), "127.0.0.1"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )
    assert server.stdout is not None and server.stderr is not None
    stdout_lines: list[str] = []
    stderr_lines: list[str] = []

    def drain_stderr() -> None:
        for line in server.stderr:
            stderr_lines.append(line.rstrip())

    threading.Thread(target=drain_stderr, daemon=True).start()
    ready = False
    deadline = time.monotonic() + 20
    while time.monotonic() < deadline:
        line = server.stdout.readline()
        if line:
            stdout_lines.append(line.rstrip())
            if "Debug server listening at" in line:
                ready = True
                break
        elif server.poll() is not None:
            break
        else:
            time.sleep(0.1)

    children: list[subprocess.Popen[Any]] = []

    def run_in_terminal(req: dict[str, Any]) -> dict[str, Any] | None:
        if req.get("command") != "runInTerminal":
            return None
        arguments = req.get("arguments", {})
        cmd = arguments.get("args") or []
        env = os.environ.copy()
        env.update(arguments.get("env") or {})
        child = subprocess.Popen(
            cmd,
            cwd=arguments.get("cwd") or str(target_dir),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        children.append(child)
        return {"processId": child.pid}

    try:
        if not ready:
            raise RuntimeError("js-debug server did not announce readiness")
        session, transcript, _ = execute_dap_session(
            [],
            {
                "clientID": "qps-triage",
                "clientName": "QPS TRIAGE",
                "adapterID": "pwa-node",
                "pathFormat": "path",
                "linesStartAt1": True,
                "columnsStartAt1": True,
                "supportsRunInTerminalRequest": True,
                "supportsStartDebuggingRequest": False,
            },
            {
                "name": "QPS js-debug",
                "type": "pwa-node",
                "request": "launch",
                "program": str(target),
                "cwd": str(target_dir),
                "console": "externalTerminal",
                "stopOnEntry": True,
                "sourceMaps": False,
            },
            request_handler=run_in_terminal,
            connect=("127.0.0.1", port),
            timeout=60,
        )
        status = "ACCEPT" if session.get("accepted") else "REJECT"
        reason = None
    except Exception as exc:
        session = {"accepted": False}
        transcript = []
        status = "DEFER"
        reason = repr(exc)
    finally:
        for child in children:
            if child.poll() is None:
                child.terminate()
        server.terminate()
        try:
            server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server.kill()

    child_output = []
    for child in children:
        try:
            out, _ = child.communicate(timeout=2)
        except subprocess.TimeoutExpired:
            child.kill()
            out, _ = child.communicate()
        if out:
            child_output.append(out[-4000:])

    body = {
        "schema": "qps.perpetual.js_debug.v2",
        "status": status,
        "dov_status": "PASS" if status == "ACCEPT" else "WITHHELD",
        "server_path": args.server_path,
        "server_port": port,
        "server_ready": ready,
        "reason": reason,
        "session": session,
        "server_stdout": stdout_lines[-40:],
        "server_stderr": stderr_lines[-80:],
        "child_output": child_output,
        "transcript_tail": transcript[-160:],
    }
    write_receipt("js_debug_live", body)
    return 0 if status == "ACCEPT" else 2


if __name__ == "__main__":
    raise SystemExit(main())
