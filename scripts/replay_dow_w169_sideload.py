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



def replay_runtime() -> dict:
    """Read-only native-source byte challenge: no KEB self-auth of GitHub results."""
    original = ROOT / "federation/sideload/fixtures/W169_QPLANT_K8S_RUNTIME_RECEIPT.json"
    provenance = json.loads((ROOT / "federation/sideload/W169_NATIVE_PROVENANCE_v1.json").read_text(encoding="utf-8"))
    envelope = json.loads((ROOT / "federation/sideload/fixtures/W169_K8S_WORKLOAD_ENVELOPE_v1.json").read_text(encoding="utf-8"))
    import re
    if provenance.get("schema") != "codex.keb.dow.w169.native-replay-provenance.v1":
        raise ValueError("source provenance changed")
    if provenance.get("source_repo") != "GBOGEB/ABACUS" or provenance.get("source_sha") != "4d8240082f532c13d5cfb240747b04caed13e5bf":
        raise ValueError("source owner or exact head changed")
    if any(provenance.get(k) != v for k,v in (
        ("run_id", 38774568289), ("job_id", 116558746360), ("attempt", 1),
        ("artifact_id", 11993466494)
    )):
        raise ValueError("run/job/attempt identity changed")
    if provenance.get("qps_disposition") != "DEFER" or provenance.get("release") != "HOLD" or provenance.get("authority_transfer") is not False or provenance.get("engineering_credit_delta") != 0:
        raise ValueError("source authority was improperly promoted")
    raw = original.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != provenance["receipt_sha256"] or len(raw) != provenance["receipt_size_bytes"]:
        raise ValueError("original public Actions receipt SHA256/size mismatch")
    source = json.loads(raw)
    if source.get("schema") != "qplant-k8s-real-api-runtime-receipt/v1" or source.get("source_sha") != provenance["source_sha"]:
        raise ValueError("native source identity mismatch")
    if source.get("real_kubernetes_api") != "success" or source.get("workload_rollout") != "success" or source.get("health_measurement") != "success":
        raise ValueError("source does not support runtime success")
    native = envelope.get("native", {})
    if envelope.get("producer", {}).get("sha") != provenance["source_sha"] or envelope.get("source", {}).get("sha256") != digest or native.get("run_id") != provenance["run_id"] or native.get("job_id") != provenance["job_id"] or native.get("attempt") != 1 or native.get("executed_steps") != 15:
        raise ValueError("transport/source identity mismatch")
    spec = importlib.util.spec_from_file_location("keb_sideload", VALIDATOR)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    receipt = module.inspect(envelope, original.parent)
    if receipt["structural"] != "PASS" or receipt["byte_binding"] != "LOCAL_HASH_MATCH_ONLY":
        raise ValueError("byte challenge not proven")
    if receipt["native_authenticated"] or receipt["k8s_workload_verified"] or receipt["k8s_api_verified"] or receipt["qps_child_disposition"] != "DEFER":
        raise ValueError("transport cannot self-grant source acceptance")
    return {"schema":"codex.keb.dow-w169.native-replay.v1","producer_sha":provenance["source_sha"],
            "run_id":provenance["run_id"],"job_id":provenance["job_id"],"attempt":1,
            "source_sha256":digest,"artifact_zip_sha256":provenance["zip_sha256"],
            "source_exact_bytes":"LOCAL_HASH_MATCH_ONLY","structural":"PASS",
            "runtime_source_status":"HISTORICAL_NATIVE_SUCCESS_PIN",
            "native_authenticated_by_keb":False,"k8s_api_verified_by_keb":False,
            "qps_child_disposition":"DEFER","admission":"HOLD",
            "authority_transfer":False,"engineering_credit_delta":0,
            "transport_receipt":receipt}


if __name__ == "__main__":
    a = argparse.ArgumentParser()
    a.add_argument("--out", type=Path, required=True)
    args = a.parse_args()
    result = replay()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["structural"], "byte_binding": result["byte_binding"], "admission": "HOLD"}))
