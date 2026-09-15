#!/usr/bin/env python3
"""Live protocol probes for the QPS perpetual-debug closure wave.

Modes:
- lldb-dap: execute the exact mirrored QPS Swift payload through DAP.
- debugpy: execute a Python target through the debugpy DAP adapter.
- js-debug: execute a Node target through a running vscode-js-debug DAP server.
- mcp: exercise lldb-mcp over stdio, including a real LLDB session command.

All receipts are maintenance/runtime evidence only. They never transfer formal
engineering or negotiation authority.
"""
from __future__ import annotations

import argparse
import json
import os
import queue
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts/qps_debug/perpetual"
MANIFEST = ROOT / "runtime/debug/federation/qps_federated_payload_manifest.json"


def now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def run(args: list[str], timeout: int = 120, cwd: Path | None = None) -> dict[str, Any]:
    proc = subprocess.run(
        args,
        cwd=cwd or ROOT,
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
    )
    return {
        "cmd": args,
        "returncode": proc.returncode,
        "stdout": proc.stdout[-12000:],
        "stderr": proc.stderr[-12000:],
    }


def resolve_tool(*names: str) -> tuple[str | None, str]:
    for name in names:
        direct = shutil.which(name)
        if direct:
            return direct, "PATH"
    xcrun = shutil.which("xcrun")
    if xcrun:
        for name in names:
            probe = run([xcrun, "--find", name], 30)
            candidate = probe.get("stdout", "").strip()
            if probe.get("returncode") == 0 and candidate:
                return candidate, "XCRUN"
    return None, "NOT_FOUND"


class FramedDAP:
    def __init__(
        self,
        reader: Any,
        writer: Any,
        request_handler: Callable[[dict[str, Any]], dict[str, Any] | None] | None = None,
    ) -> None:
        self.reader = reader
        self.writer = writer
        self.request_handler = request_handler
        self.seq = 1
        self.messages: queue.Queue[dict[str, Any]] = queue.Queue()
        self.backlog: list[dict[str, Any]] = []
        self.transcript: list[dict[str, Any]] = []
        self._thread = threading.Thread(target=self._read_loop, daemon=True)
        self._thread.start()

    def _read_loop(self) -> None:
        try:
            while True:
                headers: dict[str, str] = {}
                while True:
                    line = self.reader.readline()
                    if not line:
                        return
                    if isinstance(line, bytes):
                        line = line.decode("utf-8", errors="replace")
                    if line in ("\r\n", "\n", ""):
                        break
                    key, _, value = line.partition(":")
                    if key and value:
                        headers[key.strip().lower()] = value.strip()
                length = int(headers.get("content-length", "0"))
                if length <= 0:
                    continue
                raw = self.reader.read(length)
                if isinstance(raw, bytes):
                    raw = raw.decode("utf-8", errors="replace")
                self.messages.put(json.loads(raw))
        except Exception as exc:  # pragma: no cover - receipt captures failure
            self.messages.put({"type": "reader_error", "error": repr(exc)})

    def send(self, message: dict[str, Any]) -> None:
        raw = json.dumps(message, separators=(",", ":")).encode("utf-8")
        self.writer.write(f"Content-Length: {len(raw)}\r\n\r\n".encode("ascii") + raw)
        self.writer.flush()
        self.transcript.append({"direction": "send", "message": message})

    def request(self, command: str, arguments: dict[str, Any] | None = None) -> int:
        seq = self.seq
        self.seq += 1
        self.send(
            {
                "seq": seq,
                "type": "request",
                "command": command,
                "arguments": arguments or {},
            }
        )
        return seq

    def respond(self, request: dict[str, Any], success: bool, body: dict[str, Any] | None = None) -> None:
        self.send(
            {
                "seq": self.seq,
                "type": "response",
                "request_seq": request.get("seq"),
                "command": request.get("command"),
                "success": success,
                "body": body or {},
            }
        )
        self.seq += 1

    def _next(self, timeout: float) -> dict[str, Any]:
        deadline = time.monotonic() + timeout
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError("DAP message timeout")
            msg = self.messages.get(timeout=remaining)
            self.transcript.append({"direction": "recv", "message": msg})
            if msg.get("type") == "request" and self.request_handler:
                reply = self.request_handler(msg)
                self.respond(msg, reply is not None, reply or {})
                continue
            return msg

    def wait(self, predicate: Callable[[dict[str, Any]], bool], timeout: float = 30) -> dict[str, Any]:
        for idx, msg in enumerate(self.backlog):
            if predicate(msg):
                return self.backlog.pop(idx)
        deadline = time.monotonic() + timeout
        while True:
            msg = self._next(max(0.1, deadline - time.monotonic()))
            if predicate(msg):
                return msg
            self.backlog.append(msg)

    def wait_response(self, seq: int, timeout: float = 30) -> dict[str, Any]:
        return self.wait(
            lambda m: m.get("type") == "response" and m.get("request_seq") == seq,
            timeout,
        )

    def wait_event(self, event: str, timeout: float = 30) -> dict[str, Any]:
        return self.wait(
            lambda m: m.get("type") == "event" and m.get("event") == event,
            timeout,
        )


def execute_dap_session(
    adapter_cmd: list[str],
    initialize_args: dict[str, Any],
    launch_args: dict[str, Any],
    request_handler: Callable[[dict[str, Any]], dict[str, Any] | None] | None = None,
    connect: tuple[str, int] | None = None,
    timeout: float = 40,
) -> tuple[dict[str, Any], list[dict[str, Any]], subprocess.Popen[Any] | None]:
    process: subprocess.Popen[Any] | None = None
    sock: socket.socket | None = None
    if connect:
        sock = socket.create_connection(connect, timeout=10)
        reader = sock.makefile("rb", buffering=0)
        writer = sock.makefile("wb", buffering=0)
    else:
        process = subprocess.Popen(
            adapter_cmd,
            cwd=ROOT,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        assert process.stdin is not None and process.stdout is not None
        reader = process.stdout
        writer = process.stdin

    dap = FramedDAP(reader, writer, request_handler=request_handler)
    result: dict[str, Any] = {}
    try:
        init_seq = dap.request("initialize", initialize_args)
        init = dap.wait_response(init_seq, timeout)
        result["initialize_success"] = init.get("success") is True

        launch_seq = dap.request("launch", launch_args)
        initialized = dap.wait_event("initialized", timeout)
        result["initialized_event"] = initialized.get("event") == "initialized"

        config_seq = dap.request("configurationDone", {})
        config = dap.wait_response(config_seq, timeout)
        launch = dap.wait_response(launch_seq, timeout)
        result["configuration_done_success"] = config.get("success") is True
        result["launch_success"] = launch.get("success") is True

        stopped = dap.wait_event("stopped", timeout)
        thread_id = stopped.get("body", {}).get("threadId")
        result["stopped_event"] = True
        result["thread_id"] = thread_id

        stack_seq = dap.request("stackTrace", {"threadId": thread_id})
        stack = dap.wait_response(stack_seq, timeout)
        frames = stack.get("body", {}).get("stackFrames", []) if stack.get("success") else []
        result["stack_trace_success"] = stack.get("success") is True
        result["stack_frames"] = len(frames)

        continue_seq = dap.request("continue", {"threadId": thread_id})
        cont = dap.wait_response(continue_seq, timeout)
        result["continue_success"] = cont.get("success") is True

        try:
            term = dap.wait(
                lambda m: m.get("type") == "event"
                and m.get("event") in {"terminated", "exited"},
                timeout,
            )
            result["terminal_event"] = term.get("event")
        except TimeoutError:
            result["terminal_event"] = None

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
    finally:
        if sock:
            try:
                sock.close()
            except OSError:
                pass
        if process:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
    return result, dap.transcript[-160:], process


def write_receipt(name: str, body: dict[str, Any]) -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    body.setdefault("created_utc", now())
    body.setdefault(
        "authority_guards",
        {
            "qps_repo_local_runner_gate": "WITHHELD_EXTERNAL",
            "formal_engineering_credit_delta": 0,
            "negotiation_credit_delta": 0,
        },
    )
    path = OUT / f"{name}.json"
    path.write_text(json.dumps(body, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(body, indent=2, sort_keys=True))
    return path


def probe_lldb_dap() -> str:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    source = ROOT / manifest["mirrored_path"]
    swiftc, swift_source = resolve_tool("swiftc")
    adapter, adapter_source = resolve_tool("lldb-dap", "lldb-vscode")
    if not swiftc or not adapter:
        status = "DEFER"
        write_receipt(
            "lldb_dap_live",
            {
                "schema": "qps.perpetual.lldb_dap.v1",
                "status": status,
                "reason": "swiftc_or_lldb_dap_missing",
                "swiftc": swiftc,
                "adapter": adapter,
            },
        )
        return status
    with tempfile.TemporaryDirectory(prefix="qps-lldb-dap-") as td:
        binary = Path(td) / "qps_probe"
        comp = run([swiftc, "-g", "-parse-as-library", str(source), "-o", str(binary)])
        if comp["returncode"] != 0:
            status = "REJECT"
            session = {"compile": comp}
            transcript: list[dict[str, Any]] = []
        else:
            session, transcript, _ = execute_dap_session(
                [adapter],
                {
                    "clientID": "qps-triage",
                    "clientName": "QPS TRIAGE",
                    "adapterID": "lldb",
                    "pathFormat": "path",
                    "linesStartAt1": True,
                    "columnsStartAt1": True,
                    "supportsRunInTerminalRequest": False,
                },
                {
                    "program": str(binary),
                    "cwd": str(ROOT),
                    "stopOnEntry": True,
                },
            )
            status = "ACCEPT" if session.get("accepted") else "REJECT"
            session["compile"] = comp
        write_receipt(
            "lldb_dap_live",
            {
                "schema": "qps.perpetual.lldb_dap.v1",
                "status": status,
                "dov_status": "PASS" if status == "ACCEPT" else "WITHHELD",
                "source_exact_sha": manifest["source_exact_sha"],
                "adapter": adapter,
                "adapter_resolution": adapter_source,
                "swiftc_resolution": swift_source,
                "session": session,
                "transcript_tail": transcript,
            },
        )
        return status


def probe_debugpy() -> str:
    target_dir = Path(tempfile.mkdtemp(prefix="qps-debugpy-"))
    target = target_dir / "probe.py"
    target.write_text("seed=41\nobserved=seed+1\nprint(f'observed={observed}', flush=True)\n", encoding="utf-8")
    session, transcript, _ = execute_dap_session(
        [sys.executable, "-m", "debugpy.adapter"],
        {
            "clientID": "qps-triage",
            "clientName": "QPS TRIAGE",
            "adapterID": "python",
            "pathFormat": "path",
            "linesStartAt1": True,
            "columnsStartAt1": True,
            "supportsRunInTerminalRequest": False,
        },
        {
            "name": "QPS debugpy",
            "type": "python",
            "request": "launch",
            "program": str(target),
            "cwd": str(target_dir),
            "console": "internalConsole",
            "redirectOutput": True,
            "stopOnEntry": True,
            "justMyCode": False,
        },
    )
    output = "\n".join(
        str(x.get("message", {}).get("body", {}).get("output", ""))
        for x in transcript
        if x.get("message", {}).get("event") == "output"
    )
    session["observed_output_42"] = "observed=42" in output
    status = "ACCEPT" if session.get("accepted") else "REJECT"
    write_receipt(
        "debugpy_live",
        {
            "schema": "qps.perpetual.debugpy.v1",
            "status": status,
            "dov_status": "PASS" if status == "ACCEPT" else "WITHHELD",
            "session": session,
            "transcript_tail": transcript,
        },
    )
    return status


def probe_js_debug(server_path: str) -> str:
    target_dir = Path(tempfile.mkdtemp(prefix="qps-js-debug-"))
    target = target_dir / "probe.js"
    target.write_text("const seed=41; const observed=seed+1; console.log(`observed=${observed}`);\n", encoding="utf-8")
    port_sock = socket.socket()
    port_sock.bind(("127.0.0.1", 0))
    port = port_sock.getsockname()[1]
    port_sock.close()
    server = subprocess.Popen(
        ["node", server_path, str(port), "127.0.0.1"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=False,
    )
    children: list[subprocess.Popen[Any]] = []

    def run_in_terminal(req: dict[str, Any]) -> dict[str, Any] | None:
        if req.get("command") != "runInTerminal":
            return None
        args = req.get("arguments", {})
        cmd = args.get("args") or []
        env = os.environ.copy()
        env.update(args.get("env") or {})
        child = subprocess.Popen(cmd, cwd=args.get("cwd") or str(target_dir), env=env)
        children.append(child)
        return {"processId": child.pid}

    try:
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline:
            try:
                with socket.create_connection(("127.0.0.1", port), timeout=0.5):
                    break
            except OSError:
                if server.poll() is not None:
                    raise RuntimeError("js-debug server exited before accepting connections")
                time.sleep(0.2)
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
    write_receipt(
        "js_debug_live",
        {
            "schema": "qps.perpetual.js_debug.v1",
            "status": status,
            "dov_status": "PASS" if status == "ACCEPT" else "WITHHELD",
            "server_path": server_path,
            "server_port": port,
            "reason": reason,
            "session": session,
            "transcript_tail": transcript,
        },
    )
    return status


def probe_mcp() -> str:
    binary, resolution = resolve_tool("lldb-mcp")
    if not binary:
        write_receipt(
            "lldb_mcp_live",
            {
                "schema": "qps.perpetual.lldb_mcp.v1",
                "status": "DEFER",
                "dov_status": "WITHHELD",
                "reason": "lldb-mcp not present on this runner/toolchain",
                "binary_resolution": resolution,
                "bd_id": "BD04-MCP-TOOLCHAIN",
            },
        )
        return "DEFER"
    proc = subprocess.Popen(
        [binary],
        cwd=ROOT,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )
    assert proc.stdin is not None and proc.stdout is not None
    transcript: list[dict[str, Any]] = []

    def send(obj: dict[str, Any]) -> None:
        proc.stdin.write(json.dumps(obj, separators=(",", ":")) + "\n")
        proc.stdin.flush()
        transcript.append({"direction": "send", "message": obj})

    def recv(expected_id: int, timeout: float = 20) -> dict[str, Any]:
        q: queue.Queue[str] = queue.Queue()

        def reader() -> None:
            line = proc.stdout.readline()
            q.put(line)

        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            thread = threading.Thread(target=reader, daemon=True)
            thread.start()
            line = q.get(timeout=max(0.1, deadline - time.monotonic()))
            if not line:
                raise RuntimeError("lldb-mcp closed stdout")
            msg = json.loads(line)
            transcript.append({"direction": "recv", "message": msg})
            if msg.get("id") == expected_id:
                return msg
        raise TimeoutError(f"lldb-mcp response timeout for id {expected_id}")

    try:
        send(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "qps-triage", "version": "1"},
                },
            }
        )
        init = recv(1)
        send({"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}})
        send({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
        tools = recv(2)
        tool_names = sorted(
            t.get("name")
            for t in tools.get("result", {}).get("tools", [])
            if isinstance(t, dict) and t.get("name")
        )
        send(
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {"name": "session_create", "arguments": {}},
            }
        )
        created = recv(3)
        created_text = json.dumps(created)
        match = re.search(r"lldb-mcp://[^\"\\\s]+", created_text)
        session_uri = match.group(0) if match else None
        if not session_uri:
            raise RuntimeError("session_create returned no lldb-mcp URI")
        send(
            {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {
                    "name": "command",
                    "arguments": {"command": "version", "debugger": session_uri},
                },
            }
        )
        command = recv(4)
        send(
            {
                "jsonrpc": "2.0",
                "id": 5,
                "method": "tools/call",
                "params": {"name": "session_close", "arguments": {"session": session_uri}},
            }
        )
        closed = recv(5)
        command_text = json.dumps(command).lower()
        expected_tools = {"session_create", "command", "sessions_list", "session_close"}
        accepted = (
            "result" in init
            and expected_tools.issubset(set(tool_names))
            and "lldb" in command_text
            and "result" in closed
        )
        status = "ACCEPT" if accepted else "REJECT"
        reason = None
    except Exception as exc:
        status = "REJECT"
        reason = repr(exc)
        tool_names = []
        session_uri = None
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
    write_receipt(
        "lldb_mcp_live",
        {
            "schema": "qps.perpetual.lldb_mcp.v1",
            "status": status,
            "dov_status": "PASS" if status == "ACCEPT" else "WITHHELD",
            "binary": binary,
            "binary_resolution": resolution,
            "tool_names": tool_names,
            "session_uri": session_uri,
            "reason": reason,
            "transcript_tail": transcript[-80:],
        },
    )
    return status


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["lldb-dap", "debugpy", "js-debug", "mcp"])
    parser.add_argument("--server-path")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    if args.mode == "lldb-dap":
        status = probe_lldb_dap()
    elif args.mode == "debugpy":
        status = probe_debugpy()
    elif args.mode == "js-debug":
        if not args.server_path:
            raise SystemExit("--server-path is required for js-debug")
        status = probe_js_debug(args.server_path)
    else:
        status = probe_mcp()
    if args.strict and status != "ACCEPT":
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
