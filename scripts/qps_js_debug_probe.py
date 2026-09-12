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
from typing import Any

from qps_debug_protocol_probe import FramedDAP, write_receipt


def execute_js_debug_session(
    host: str,
    port: int,
    initialize_args: dict[str, Any],
    launch_args: dict[str, Any],
    timeout: float = 60,
) -> tuple[dict[str, Any], list[dict[str, Any]], str, str | None]:
    """Execute js-debug while preserving the exact wait stage on failure."""
    sock = socket.create_connection((host, port), timeout=10)
    reader = sock.makefile("rb")
    writer = sock.makefile("wb")
    dap = FramedDAP(reader, writer)
    result: dict[str, Any] = {}
    stage = "initialize_response"
    reason: str | None = None
    try:
        init_seq = dap.request("initialize", initialize_args)
        init = dap.wait_response(init_seq, timeout)
        result["initialize_success"] = init.get("success") is True

        stage = "initialized_event"
        launch_seq = dap.request("launch", launch_args)
        initialized = dap.wait_event("initialized", timeout)
        result["initialized_event"] = initialized.get("event") == "initialized"

        stage = "configuration_done_response"
        config_seq = dap.request("configurationDone", {})
        config = dap.wait_response(config_seq, timeout)
        result["configuration_done_success"] = config.get("success") is True

        stage = "launch_response"
        launch = dap.wait_response(launch_seq, timeout)
        result["launch_success"] = launch.get("success") is True

        stage = "stopped_event"
        stopped = dap.wait_event("stopped", timeout)
        thread_id = stopped.get("body", {}).get("threadId")
        result["stopped_event"] = True
        result["thread_id"] = thread_id

        stage = "stack_trace_response"
        stack_seq = dap.request("stackTrace", {"threadId": thread_id})
        stack = dap.wait_response(stack_seq, timeout)
        frames = (
            stack.get("body", {}).get("stackFrames", [])
            if stack.get("success")
            else []
        )
        result["stack_trace_success"] = stack.get("success") is True
        result["stack_frames"] = len(frames)

        stage = "continue_response"
        continue_seq = dap.request("continue", {"threadId": thread_id})
        cont = dap.wait_response(continue_seq, timeout)
        result["continue_success"] = cont.get("success") is True

        stage = "terminal_event"
        try:
            term = dap.wait(
                lambda m: m.get("type") == "event"
                and m.get("event") in {"terminated", "exited"},
                timeout,
            )
            result["terminal_event"] = term.get("event")
        except Exception as exc:
            result["terminal_event"] = None
            reason = repr(exc)

        result["accepted"] = all(
            [
                result.get("initialize_success"),
                result.get("initialized_event"),
                result.get("configuration_done_success"),
                result.get("launch_success"),
                result.get("stopped_event"),
                result.get("stack_trace_success"),
                result.get("stack_frames", 0) > 0,
                result.get("continue_success"),
            ]
        )
        if result["accepted"]:
            stage = "complete"
    except Exception as exc:
        reason = repr(exc)
        result["accepted"] = False
    finally:
        try:
            writer.close()
        except OSError:
            pass
        try:
            reader.close()
        except OSError:
            pass
        try:
            sock.close()
        except OSError:
            pass
    return result, dap.transcript[-160:], stage, reason


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
        session, transcript, failure_stage, reason = execute_js_debug_session(
            "127.0.0.1",
            port,
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
            timeout=60,
        )
        output = "\n".join(
            str(x.get("message", {}).get("body", {}).get("output", ""))
            for x in transcript
            if x.get("message", {}).get("event") == "output"
        )
        session["observed_output_42"] = "observed=42" in output
        accepted = session.get("accepted") and session["observed_output_42"]
        status = "ACCEPT" if accepted else "DEFER"
        if accepted:
            reason = None
            failure_stage = "complete"
    except Exception as exc:
        session = {"accepted": False, "observed_output_42": False}
        transcript = []
        status = "DEFER"
        reason = repr(exc)
        failure_stage = "server_startup"
    finally:
        server.terminate()
        try:
            server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server.kill()

    body = {
        "schema": "qps.perpetual.js_debug.v4",
        "status": status,
        "dov_status": "PASS" if status == "ACCEPT" else "WITHHELD",
        "server_path": args.server_path,
        "server_port": port,
        "server_ready": ready,
        "failure_stage": failure_stage,
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
