#!/usr/bin/env python3
"""CODEX-owned MYCELIUM read-only consumer of QPS Dependency SPINE stage receipts.

An observed private producer artifact must be presented via an owner-approved
local path. This module never contacts other repositories, dispatches or mutates.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

SHA = re.compile(r"^[0-9a-f]{40}$")
SCHEMA = "codex.mycelium.dependency_spine.stage.v1"
SOURCE_REPO = "GBOGEB/cryoplant-project"

def pack(value: dict) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True)+"\n").encode()

def checksum(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def head(root: Path) -> str:
    p = subprocess.run(["git","rev-parse","--verify","HEAD"],cwd=root,text=True,capture_output=True,check=False)
    return p.stdout.strip() if p.returncode == 0 else ""

def check_gateway(root: Path) -> None:
    gateway=root/"mission_control"/"mycelium"/"execution_gateway_contract.yaml"
    if not gateway.is_file():
        raise ValueError("OWNER_GATEWAY_MISSING")
    contract=gateway.read_text(encoding="utf-8")
    for requirement in ("STAGE_ONLY:", "mutation_enabled: false", "remote_mutation_default: DENY", "enabled_mutation_transports: []"):
        if requirement not in contract:
            raise ValueError("OWNER_GATEWAY_NOT_FAIL_CLOSED")

def validate_producer(task: dict, receipt: dict, manifest: dict, expected_qps_sha: str) -> str:
    if not SHA.fullmatch(expected_qps_sha):
        raise ValueError("BAD_QPS_SHA")
    if task.get("schema") != "qps.dependency_spine.stage_request/1.0":
        raise ValueError("TASK_SCHEMA")
    if receipt.get("schema") != "qps.dependency_spine.census/1.0":
        raise ValueError("CENSUS_SCHEMA")
    if manifest.get("schema") != "qps.dependency_spine.sha256/1.0":
        raise ValueError("SOURCE_MANIFEST_SCHEMA")
    if task.get("source_repo")!=SOURCE_REPO or task.get("source_sha")!=expected_qps_sha:
        raise ValueError("SOURCE_IDENTITY")
    if manifest.get("source_shas",{}).get(SOURCE_REPO)!=expected_qps_sha:
        raise ValueError("SOURCE_MANIFEST_HEAD")
    if receipt.get("repositories",{}).get(SOURCE_REPO,{}).get("source_sha")!=expected_qps_sha:
        raise ValueError("CENSUS_HEAD")
    dg=checksum(pack(receipt))
    if task.get("receipt_sha256")!=dg:
        raise ValueError("SOURCE_CENSUS_DIGEST")
    if manifest.get("files",{}).get("QPS_DEPENDENCY_SPINE_RECEIPT.json") != dg:
        raise ValueError("SOURCE_MANIFEST_DIGEST")
    key={k:v for k,v in task.items() if k!="idempotency_key"}
    if task.get("idempotency_key")!=checksum(pack(key)):
        raise ValueError("BAD_IDEMPOTENCY_KEY")
    if (task.get("gateway")!="CODEX_MYCELIUM_STAGE_ONLY" or task.get("action_class")!="STAGE_ONLY"
            or task.get("dispatch_authorized") is not False or task.get("mutation_enabled") is not False
            or task.get("review_approval_present") is not False or task.get("merge_admission")!="HOLD"
            or task.get("formal_credit_delta")!=0 or task.get("qps_disposition")!="DEFER"):
        raise ValueError("PRODUCER_AUTHORITY_ESCALATION")
    guards=receipt.get("governance",{})
    if (guards.get("authority_transfer") is not False or guards.get("remote_dispatch_authorized") is not False
            or guards.get("merge_admission")!="HOLD" or guards.get("qps_child_disposition")!="DEFER"
            or guards.get("engineering_credit_delta")!=0):
        raise ValueError("PRODUCER_GOVERNANCE")
    return dg

def stage(source_dir: Path | None, expected_qps_sha: str | None, consumer_sha: str) -> dict:
    if not SHA.fullmatch(consumer_sha):
        raise ValueError("CONSUMER_HEAD_INVALID")
    producer_digest=None
    if source_dir is not None:
        if expected_qps_sha is None:
            raise ValueError("EXPECTED_SOURCE_SHA_REQUIRED")
        files=("QPS_DEPENDENCY_SPINE_TASK.json","QPS_DEPENDENCY_SPINE_RECEIPT.json","QPS_DEPENDENCY_SPINE_SHA256.json")
        try:
            task, receipt, manifest=[json.loads((source_dir/name).read_text(encoding="utf-8")) for name in files]
        except (OSError,ValueError) as e:
            raise ValueError("SOURCE_ARTIFACT_UNAVAILABLE_OR_INVALID") from e
        producer_digest=validate_producer(task,receipt,manifest,expected_qps_sha)
    result={
        "schema":SCHEMA,"consumer_repo":"GBOGEB/CODEX","consumer_head_sha":consumer_sha,
        "source_repo":SOURCE_REPO,"source_head_sha":expected_qps_sha if producer_digest else None,
        "source_receipt_sha256":producer_digest,
        "stage_status":"STAGE_ONLY_VALIDATED_NO_AUTHENTICATED_CONSUMER_PROOF" if producer_digest else "DEFER_SOURCE_ARTIFACT_NOT_STAGED",
        "child_disposition":"DEFER","authenticated_remote_execution":False,
        "native_producer_run_job_attempt_bound":False,
        "formal_credit_delta":0,"authority_transfer":False,"mutation_enabled":False,
        "dispatch_authorized":False,"merge_admission":"HOLD",
        "next_owner":"ABACUS_DELTA_1_AFTER_AUTHENTICATED_REVIEW",
    }
    result["stage_digest_sha256"]=checksum(pack(result))
    return result

def verify(result: dict) -> None:
    unsigned={k:v for k,v in result.items() if k!="stage_digest_sha256"}
    if result.get("stage_digest_sha256")!=checksum(pack(unsigned)):
        raise ValueError("RESULT_DIGEST_MISMATCH")
    if (result.get("schema")!=SCHEMA or result.get("child_disposition")!="DEFER"
        or result.get("authenticated_remote_execution") is not False
        or result.get("native_producer_run_job_attempt_bound") is not False
        or result.get("dispatch_authorized") is not False or result.get("mutation_enabled") is not False
        or result.get("authority_transfer") is not False or result.get("formal_credit_delta")!=0
        or result.get("merge_admission")!="HOLD"):
        raise ValueError("CODEX_PROMOTION_FORBIDDEN")

def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--root",type=Path,default=Path("."))
    p.add_argument("--consumer-sha",required=True)
    p.add_argument("--source-dir",type=Path)
    p.add_argument("--qps-sha")
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    if head(a.root)!=a.consumer_sha:
        raise SystemExit("EXACT_CONSUMER_SHA_MISMATCH")
    check_gateway(a.root)
    receipt=stage(a.source_dir,a.qps_sha,a.consumer_sha)
    verify(receipt)
    a.out.mkdir(parents=True,exist_ok=True)
    (a.out/"CODEX_DEPENDENCY_SPINE_STAGE.json").write_bytes(pack(receipt))
    print(json.dumps({"status":receipt["stage_status"],"merge_admission":"HOLD","formal_credit_delta":0},sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
