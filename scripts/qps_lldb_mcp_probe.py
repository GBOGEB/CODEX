#!/usr/bin/env python3
"""Prove official LLVM lldb-mcp against its versioned tool contract.

LLVM 23.1.x exposes the registry-backed `command` and `sessions_list` tools.
Newer managed-session builds additionally expose `session_create` and
`session_close`. Both profiles must execute a real `version` command against
an `lldb-mcp://` debugger URI; managed builds must also create and close the
session they own.
"""
from __future__ import annotations

import json
import queue
import re
import subprocess
import threading
import time
from typing import Any

from qps_debug_protocol_probe import ROOT, resolve_tool, write_receipt

RELEASE_TOOLS = {"command", "sessions_list"}
MANAGED_TOOLS = RELEASE_TOOLS | {"session_create", "session_close"}


def debugger_uri(message: dict[str, Any]) -> str | None:
    match = re.search(
        r"lldb-mcp://instance/\d+/debugger/\d+",
        json.dumps(message),
    )
    return match.group(0) if match else None


def text_content(message: dict[str, Any]) -> str:
    return "\n".join(
        item["text"]
        for item in message.get("result", {}).get("content", [])
        if isinstance(item, dict) and isinstance(item.get("text"), str)
    )


def main() -> int:
    binary, resolution = resolve_tool("lldb-mcp")
    if not binary:
        write_receipt(
            "lldb_mcp_live",
            {
                "schema": "qps.perpetual.lldb_mcp.v2",
                "status": "DEFER",
                "dov_status": "WITHHELD",
                "reason": "lldb-mcp not present on this runner/toolchain",
                "binary_resolution": resolution,
                "bd_id": "BD04-MCP-TOOLCHAIN",
            },
        )
        return 2

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
    tool_names: list[str] = []
    session_uri: str | None = None
    server_version: str | None = None
    contract_profile: str | None = None
    managed_session_closed: bool | None = None

    def send(obj: dict[str, Any]) -> None:
        proc.stdin.write(json.dumps(obj, separators=(",", ":")) + "\n")
        proc.stdin.flush()
        transcript.append({"direction": "send", "message": obj})

    def recv(expected_id: int, timeout: float = 20) -> dict[str, Any]:
        q: queue.Queue[str] = queue.Queue()

        def reader() -> None:
            q.put(proc.stdout.readline())

        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            threading.Thread(target=reader, daemon=True).start()
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
        if "result" not in init:
            raise RuntimeError("initialize returned no result")
        server_info = init.get("result", {}).get("serverInfo", {})
        if server_info.get("name") != "lldb-mcp":
            raise RuntimeError(f"unexpected MCP server identity: {server_info!r}")
        server_version = str(server_info.get("version") or "")

        send(
            {
                "jsonrpc": "2.0",
                "method": "notifications/initialized",
                "params": {},
            }
        )
        send(
            {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
                "params": {},
            }
        )
        tools = recv(2)
        tool_names = sorted(
            tool.get("name")
            for tool in tools.get("result", {}).get("tools", [])
            if isinstance(tool, dict) and tool.get("name")
        )
        observed = set(tool_names)

        if MANAGED_TOOLS.issubset(observed):
            contract_profile = "llvm_managed_session_v1"
            send(
                {
                    "jsonrpc": "2.0",
                    "id": 3,
                    "method": "tools/call",
                    "params": {"name": "session_create", "arguments": {}},
                }
            )
            created = recv(3)
            session_uri = debugger_uri(created)
            if not session_uri:
                raise RuntimeError("session_create returned no lldb-mcp URI")
        elif RELEASE_TOOLS.issubset(observed) and server_version.startswith("23.1."):
            contract_profile = "llvm_release_23_1_registry_v1"
            send(
                {
                    "jsonrpc": "2.0",
                    "id": 3,
                    "method": "tools/call",
                    "params": {"name": "sessions_list", "arguments": {}},
                }
            )
            sessions = recv(3)
            session_uri = debugger_uri(sessions)
            if not session_uri:
                raise RuntimeError("sessions_list returned no global lldb-mcp URI")
        else:
            raise RuntimeError(
                "unsupported lldb-mcp tool contract: "
                f"version={server_version!r} tools={tool_names!r}"
            )

        send(
            {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {
                    "name": "command",
                    "arguments": {
                        "command": "version",
                        "debugger": session_uri,
                    },
                },
            }
        )
        command = recv(4)
        if "lldb" not in text_content(command).lower():
            raise RuntimeError("command(version) did not return LLDB identity")

        if contract_profile == "llvm_managed_session_v1":
            send(
                {
                    "jsonrpc": "2.0",
                    "id": 5,
                    "method": "tools/call",
                    "params": {
                        "name": "session_close",
                        "arguments": {"session": session_uri},
                    },
                }
            )
            closed = recv(5)
            if "result" not in closed:
                raise RuntimeError("session_close returned no result")
            managed_session_closed = True

        status = "ACCEPT"
        reason = None
    except Exception as exc:
        status = "REJECT"
        reason = repr(exc)
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()

    write_receipt(
        "lldb_mcp_live",
        {
            "schema": "qps.perpetual.lldb_mcp.v2",
            "status": status,
            "dov_status": "PASS" if status == "ACCEPT" else "WITHHELD",
            "binary": binary,
            "binary_resolution": resolution,
            "server_version": server_version,
            "contract_profile": contract_profile,
            "tool_names": tool_names,
            "session_uri": session_uri,
            "command_version_verified": status == "ACCEPT",
            "managed_session_closed": managed_session_closed,
            "reason": reason,
            "transcript_tail": transcript[-80:],
            "authority_guards": {
                "formal_engineering_credit_delta": 0,
                "negotiation_credit_delta": 0,
                "qps_repo_local_runner_gate": "WITHHELD_EXTERNAL",
            },
        },
    )
    return 0 if status == "ACCEPT" else 2


if __name__ == "__main__":
    raise SystemExit(main())
