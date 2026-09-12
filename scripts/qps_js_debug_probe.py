#!/usr/bin/env python3
"""Run one real Node DAP session through the pinned vscode-js-debug server."""
from __future__ import annotations

import argparse
import socket
import subprocess
import tempfile
import threading
import time
from pathlib import Path

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

    try:
        if not ready:
            raise RuntimeError("js-debug server did not announce readiness")
        # vscode-js-debug's canonical Node launch defaults to internalConsole.
        # That lets the adapter spawn and own Node directly and removes the
        # runInTerminal mediation layer that previously attached but never
        # delivered the expected stopped event to this protocol probe.
        session, transcript, _ = execute_dap_session(
            [],
            {
                "clientID": "qps-triage",
                "clientName": "QPS TRIAGE",
                "adapterID": "pwa-node",
                "pathFormat": "path",
                "linesStartAt1": True,
                "columnsStartAt1": True,
                "supportsRunInTerminalRequest": False,
                "supportsStartDebuggingRequest": False,
            },
            {
                "name": "QPS js-debug",
                "type": "pwa-node",
                "request": "launch",
                "program": str(target),
                "cwd": str(target_dir),
                "console": "internalConsole",
                "stopOnEntry": True,
                "sourceMaps": False,
                "runtimeExecutable": "node",
                "outputCapture": "console",
            },
            request_handler=None,
            connect=("127.0.0.1", port),
            timeout=60,
        )
        output = "\n".join(
            str(x.get("message", {}).get("body", {}).get("output", ""))
            for x in transcript
            if x.get("message", {}).get("event") == "output"
        )
        session["observed_output_42"] = "observed=42" in output
        accepted = session.get("accepted") and session["observed_output_42"]
        status = "ACCEPT" if accepted else "REJECT"
        reason = None
    except Exception as exc:
        session = {"accepted": False, "observed_output_42": False}
        transcript = []
        status = "DEFER"
        reason = repr(exc)
    finally:
        server.terminate()
        try:
            server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server.kill()

    body = {
        "schema": "qps.perpetual.js_debug.v3",
        "status": status,
        "dov_status": "PASS" if status == "ACCEPT" else "WITHHELD",
        "server_path": args.server_path,
        "server_port": port,
        "server_ready": ready,
        "reason": reason,
        "session": session,
        "server_stdout": stdout_lines[-40:],
        "server_stderr": stderr_lines[-80:],
        "transcript_tail": transcript[-160:],
    }
    write_receipt("js_debug_live", body)
    return 0 if status == "ACCEPT" else 2


if __name__ == "__main__":
    raise SystemExit(main())
