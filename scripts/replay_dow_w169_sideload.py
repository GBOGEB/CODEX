#!/usr/bin/env python3
"""Reproduce a pinned DOW K8S envelope against CODEX's existing KEB validator.

Historical PR-byte fixture only. This does not authenticate native runs,
Kubernetes API or workload execution, or authorize QPS acceptance.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PIN = ROOT / "federation/sideload/DOW_W169_REPLAY_PIN_v1.json"
VALIDATOR = ROOT / "scripts/qps_sideload_v1.py"


def blob_sha(payload: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(payload)).encode() + b"\0" + payload).hexdigest()


def replay() -> dict:
    pin = json.loads(PIN.read_text(encoding="utf-8"))
    if pin.get("schema") != "codex.keb.sideload.dow-replay-pin.v1":
        raise ValueError("replay pin schema changed")
    if pin.get("snapshot_class") != "EXTERNAL_DOW_PR_SNAPSHOT_NOT_RUNTIME":
        raise ValueError("snapshot disguised as native runtime")
    if any(pin.get(key) is not None for key in (
        "native_run", "native_job", "native_attempt", "artifact_bytes_verified",
        "k8s_api_verified", "k8s_workload_verified"
    )):
        raise ValueError("self-declared native/cluster proof")
    if pin.get("disposition") != "DEFER" or pin.get("admission") != "HOLD" or pin.get("authority_transfer") is not False or pin.get("engineering_credit_delta") != 0:
        raise ValueError("authority elevation forbidden")
    if pin.get("producer") != "GBOGEB/ABACUS" or pin.get("child_owner") != "GBOGEB/cryoplant-project":
        raise ValueError("owner changed")
    source = ROOT / pin["replay_file"]
    if source.parent != ROOT / "federation/sideload/fixtures":
        raise ValueError("fixture escaped controlled directory")
    raw = source.read_bytes()
    if blob_sha(raw) != pin["source_git_blob_sha1"]:
        raise ValueError("DOW source fixture differs from exact pinned Git blob")
    obj = json.loads(raw)
    if obj["schema"] != pin["envelope_schema"] or obj["producer"]["repo"] != pin["producer"]:
        raise ValueError("DOW source identity mismatch")
    spec = importlib.util.spec_from_file_location("keb_sideload", VALIDATOR)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    receipt = module.inspect(obj)
    if receipt["structural"] != "PASS" or receipt["native_authenticated"] or receipt["k8s_api_verified"] or receipt["k8s_workload_verified"]:
        raise ValueError("replay improperly promotes runtime")
    return {
        "schema": "codex.keb.dow-w169-structural-replay.v1",
        "source_pr": pin["source_pr"],
        "source_pr_head": pin["source_pr_head"],
        "source_git_blob_sha1": pin["source_git_blob_sha1"],
        "source_file_sha256": hashlib.sha256(raw).hexdigest(),
        "structural": receipt["structural"], "byte_binding": receipt["byte_binding"],
        "native_authenticated": False, "k8s_api_verified": False,
        "k8s_workload_verified": False, "edge_parent_qualified": False,
        "qps_child_disposition": "DEFER", "admission": "HOLD",
        "transport_receipt": receipt,
        "evidence_class": "PINNED_DOW_SOURCE_LOCAL_STRUCTURAL_REPLAY_ONLY",
        "authority_transfer": False, "engineering_credit_delta": 0,
    }


if __name__ == "__main__":
    a = argparse.ArgumentParser()
    a.add_argument("--out", type=Path, required=True)
    args = a.parse_args()
    result = replay()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["structural"], "byte_binding": result["byte_binding"], "admission": "HOLD"}))
