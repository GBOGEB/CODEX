#!/usr/bin/env python3
"""Real Docker -> lldb-server -> host LLDB remote-attach proof.

Docker is an execution primitive here, not a census field. The host port is
allocated by Docker on loopback and then observed from `docker port`.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts/qps_debug/perpetual"


def run(args: list[str], timeout: int = 300, cwd: Path | None = None) -> dict[str, Any]:
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
        "stdout": proc.stdout[-16000:],
        "stderr": proc.stderr[-16000:],
    }


def receipt(body: dict[str, Any]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    body["created_utc"] = datetime.now(UTC).replace(microsecond=0).isoformat()
    body["authority_guards"] = {
        "qps_repo_local_runner_gate": "WITHHELD_EXTERNAL",
        "formal_engineering_credit_delta": 0,
        "negotiation_credit_delta": 0,
    }
    (OUT / "docker_remote_lldb.json").write_text(
        json.dumps(body, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(body, indent=2, sort_keys=True))


def main() -> int:
    docker = shutil.which("docker")
    lldb = shutil.which("lldb")
    if not docker or not lldb:
        receipt(
            {
                "schema": "qps.perpetual.docker_lldb.v1",
                "status": "DEFER",
                "dov_status": "WITHHELD",
                "reason": "docker_or_host_lldb_missing",
                "docker": docker,
                "lldb": lldb,
                "bd_id": "BD03-DOCKER-RUNTIME",
            }
        )
        return 3

    sha = os.getenv("GITHUB_SHA", "local")[:12]
    image = f"qps-perpetual-debug:{sha}"
    container_id = None
    with tempfile.TemporaryDirectory(prefix="qps-docker-debug-") as td:
        work = Path(td)
        (work / "probe.c").write_text(
            "#include <stdio.h>\nint main(void){int seed=41; int observed=seed+1; "
            "printf(\"observed=%d\\n\", observed); return observed==42?0:1;}\n",
            encoding="utf-8",
        )
        (work / "Dockerfile").write_text(
            "FROM ubuntu:24.04\n"
            "RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y "
            "clang lldb && rm -rf /var/lib/apt/lists/*\n"
            "WORKDIR /opt/qps\nCOPY probe.c .\nRUN clang -g -O0 probe.c -o probe\n"
            "EXPOSE 4711\n"
            "CMD [\"lldb-server\",\"gdbserver\",\"0.0.0.0:4711\",\"/opt/qps/probe\"]\n",
            encoding="utf-8",
        )
        build = run([docker, "build", "-t", image, "."], cwd=work)
        if build["returncode"] != 0:
            receipt({"schema": "qps.perpetual.docker_lldb.v1", "status": "REJECT", "build": build})
            return 2
        inspect = run([docker, "image", "inspect", image, "--format", "{{.Id}}"])
        start = run([docker, "run", "-d", "--rm", "-p", "127.0.0.1::4711", image])
        if start["returncode"] != 0:
            receipt({"schema": "qps.perpetual.docker_lldb.v1", "status": "REJECT", "start": start})
            return 2
        container_id = start["stdout"].strip()
        port = None
        port_observation = None
        for _ in range(40):
            port_observation = run([docker, "port", container_id, "4711/tcp"], 20)
            match = re.search(r"127\.0\.0\.1:(\d+)", port_observation.get("stdout", ""))
            if match:
                port = int(match.group(1))
                break
            time.sleep(0.25)
        if port is None:
            run([docker, "rm", "-f", container_id], 30)
            receipt(
                {
                    "schema": "qps.perpetual.docker_lldb.v1",
                    "status": "REJECT",
                    "reason": "dynamic_loopback_port_not_observed",
                    "port_observation": port_observation,
                }
            )
            return 2
        copy = run([docker, "cp", f"{container_id}:/opt/qps/probe", str(work / "probe")])
        debug = run(
            [
                lldb,
                "--batch",
                "-o",
                f"target create {work / 'probe'}",
                "-o",
                f"gdb-remote 127.0.0.1:{port}",
                "-o",
                "breakpoint set --name main",
                "-o",
                "continue",
                "-o",
                "thread step-over",
                "-o",
                "thread backtrace",
                "-o",
                "continue",
            ],
            120,
        )
        combined = debug.get("stdout", "") + "\n" + debug.get("stderr", "")
        steps = combined.count("frame #") + combined.count("stop reason")
        logs = run([docker, "logs", container_id], 30)
        cleanup = run([docker, "rm", "-f", container_id], 30)
        container_id = None
        accepted = (
            build["returncode"] == 0
            and copy["returncode"] == 0
            and debug["returncode"] == 0
            and steps > 0
            and port > 0
            and "127.0.0.1" in (port_observation or {}).get("stdout", "")
            and cleanup["returncode"] == 0
        )
        body = {
            "schema": "qps.perpetual.docker_lldb.v1",
            "status": "ACCEPT" if accepted else "REJECT",
            "dov_status": "PASS" if accepted else "WITHHELD",
            "image": image,
            "image_id": inspect.get("stdout", "").strip(),
            "container_id": start.get("stdout", "").strip(),
            "host_binding": f"127.0.0.1:{port}",
            "container_port": 4711,
            "port_allocation": "docker_dynamic_host_port",
            "build": build,
            "port_observation": port_observation,
            "copy": copy,
            "debug": debug,
            "container_logs": logs,
            "cleanup": cleanup,
            "real_probe_steps": steps,
        }
        receipt(body)
        return 0 if accepted else 2


if __name__ == "__main__":
    raise SystemExit(main())
