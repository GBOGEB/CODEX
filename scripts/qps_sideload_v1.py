#!/usr/bin/env python3
"""Read-only KEB side-load envelope inspection; never grants runtime/child approval."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "federation/sideload/CONTRACT_V1.json"
S40 = re.compile(r"^[a-f0-9]{40}$")
S64 = re.compile(r"^[a-f0-9]{64}$")
ID = re.compile(r"^[A-Z0-9][A-Z0-9_.-]{3,99}$")


def canonical(obj: dict) -> bytes:
    return (json.dumps(obj, sort_keys=True, separators=(",", ":")) + "\n").encode()


def shape(obj: object, fields: list[str], label: str) -> None:
    if not isinstance(obj, dict) or set(obj) != set(fields):
        raise ValueError(label + " invalid fields")


def safe_path(value: object) -> bool:
    if not isinstance(value, str) or not value or "\\" in value or ":" in value:
        return False
    p = Path(value)
    return not p.is_absolute() and ".." not in p.parts


def reject_raw(obj: object, blocked: set[str]) -> None:
    if isinstance(obj, dict):
        if any(str(key).lower() in blocked for key in obj):
            raise ValueError("raw or secret material forbidden")
        for val in obj.values():
            reject_raw(val, blocked)
    if isinstance(obj, list):
        for val in obj:
            reject_raw(val, blocked)


def inspect(payload: dict, artifact_root: Path | None = None) -> dict:
    c = json.loads(CONTRACT.read_text(encoding="utf-8"))
    reject_raw(payload, set(c["blocked_fields"]))
    shape(payload, c["fields"], "envelope")
    if payload["schema"] != c["envelope_schema"] or not ID.fullmatch(
        str(payload["id"])
    ):
        raise ValueError("schema or stable ID mismatch")
    for key in ("producer", "scope", "source", "native", "claims"):
        shape(payload[key], c[key + "_fields"], key)
    p, s, n = payload["producer"], payload["source"], payload["native"]
    if p["repo"] not in c["repositories"] or payload["consumer"] not in c["repositories"]:
        raise ValueError("unrecognized repository")
    if not isinstance(p["sha"], str) or not S40.fullmatch(p["sha"]):
        raise ValueError("exact producer SHA missing")
    if payload["kind"] not in c["kinds"]:
        raise ValueError("unrecognized evidence kind")
    if not safe_path(s["path"]) or not safe_path(payload["scope"]["surface"]):
        raise ValueError("unsafe relative path")
    ns = payload["scope"]["namespace"]
    if ns is not None and (
        not isinstance(ns, str)
        or not re.fullmatch(r"[a-z0-9]([-a-z0-9]{0,61}[a-z0-9])?", ns)
    ):
        raise ValueError("invalid namespace")
    digest, size = s["sha256"], s["size_bytes"]
    if (digest is None) != (size is None):
        raise ValueError("hash/size identity pair incomplete")
    if digest is not None and (
        not isinstance(digest, str) or not S64.fullmatch(digest)
        or type(size) is not int or size < 0
    ):
        raise ValueError("invalid artifact hash/size")
    for key, value in n.items():
        if value is not None and (
            type(value) is not int or value < 0 or (key != "executed_steps" and value == 0)
        ):
            raise ValueError("invalid native run/job/attempt/steps")
    if payload["claims"] != {
        "authority_transfer": False, "engineering_credit_delta": 0,
        "release_admitted": False,
    }:
        raise ValueError("authority or release forgery")
    date = payload["observed_at_utc"]
    if date is not None and (
        not isinstance(date, str)
        or not re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ", date)
    ):
        raise ValueError("UTC observation must be explicit or null")
    bytes_state = "BYTES_UNVERIFIED"
    if artifact_root is not None:
        if digest is None:
            raise ValueError("local evidence lacks declared hash and size")
        root = artifact_root.resolve(strict=True)
        target = (root / s["path"]).resolve(strict=True)
        if not target.is_relative_to(root) or not target.is_file():
            raise ValueError("local evidence escaped root")
        data = target.read_bytes()
        if hashlib.sha256(data).hexdigest() != digest or len(data) != size:
            raise ValueError("artifact hash/size mismatch")
        bytes_state = "LOCAL_HASH_MATCH_ONLY"
    return {
        "schema": "codex.keb.sideload.receipt.v1", "id": payload["id"],
        "input_sha256": hashlib.sha256(canonical(payload)).hexdigest(),
        "producer": p, "consumer": payload["consumer"], "kind": payload["kind"],
        "contract": c["version"], "structural": "PASS",
        "byte_binding": bytes_state,
        "native_metadata": n,
        "native_authenticated": False, "k8s_api_verified": False,
        "k8s_workload_verified": False, "edge_parent_qualified": False,
        "zero_step": n["executed_steps"] == 0,
        "qps_child_disposition": "DEFER", "admission": "HOLD",
        "authority_transfer": False, "engineering_credit_delta": 0,
        "formal_credit_delta": 0,
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--input", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--artifact-root", type=Path)
    a = p.parse_args()
    result = inspect(json.loads(a.input.read_text(encoding="utf-8")), a.artifact_root)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_bytes(json.dumps(result, sort_keys=True, indent=2).encode() + b"\n")
    print(json.dumps({"status": "STRUCTURAL_PASS", "admission": "HOLD"}))


if __name__ == "__main__":
    main()
