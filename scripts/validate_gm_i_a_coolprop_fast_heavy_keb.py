#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

EXPECTED_DIGEST="132ff84a3502f5ce39d4698fa772e98f7e8fba8e52587e698e8ea419197e1398"
EXPECTED_SOURCE="47cc8dced9278d50714ac39ef0a2edab7458c6a0"
EXPECTED_MERGE="9d10914924810c26a0d88f8aaea4db03b7a3d38e"
EXPECTED_RUN=35424686224

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--provider",required=True)
    ap.add_argument("--receipt",required=True)
    args=ap.parse_args()
    p=Path(args.provider)
    digest=hashlib.sha256(p.read_bytes()).hexdigest()
    if digest!=EXPECTED_DIGEST:
        raise SystemExit(f"provider digest mismatch: {digest}")
    d=json.loads(p.read_text())
    assert d["schema"]=="qps.gm_i_a.fast_heavy.federation_attestation.v1"
    assert d["mission"]=="GM-I-A"
    assert d["lane"]=="L9_FEDERATION"
    assert d["source_head_sha"]==EXPECTED_SOURCE
    assert d["source_merge_sha"]==EXPECTED_MERGE
    assert d["workflow"]["run_id"]==EXPECTED_RUN
    assert d["workflow"]["conclusion"]=="success"
    assert d["heavy"]["conclusion"]=="success"
    assert d["heavy"]["build_seconds"]>0
    assert d["fast"]["conclusion"]=="success"
    assert d["fast"]["calculations_passed"]>0
    assert d["fast"]["build_invoked"] is False
    assert d["fast"]["source_checkout_performed"] is False
    assert d["runtime_economics"]["fast_execution_is_independent_of_source_build"] is True
    a=d["authority"]
    assert a["scope"]=="COMPATIBILITY_RUNTIME_ONLY"
    assert a["authority_transfer"] is False
    assert a["engineering_promotion"]=="WITHHELD"
    out={
      "schema":"codex.keb.gm_i_a.fast_heavy.v1",
      "object_type":"KEB_KNOWLEDGE_ATOM",
      "status":"PASS",
      "provider_repo":d["provider_repo"],
      "provider_attestation_commit":"a71924147117c02ccc70c9b6436d89623897606c",
      "provider_attestation_sha256":digest,
      "provider_source_head_sha":d["source_head_sha"],
      "provider_runtime_run_id":d["workflow"]["run_id"],
      "knowledge":{
        "topic":"FAST_HEAVY_RUNTIME_ECONOMICS",
        "heavy_build_seconds":d["heavy"]["build_seconds"],
        "heavy_queue_seconds":d["heavy"]["queue_seconds"],
        "fast_execute_seconds":d["fast"]["execute_seconds"],
        "fast_queue_seconds":d["fast"]["queue_seconds"],
        "fast_calculations_passed":d["fast"]["calculations_passed"],
        "observation":"BUILD_AND_RUNNER_QUEUE_ARE_DISTINCT_RUNTIME_PRESSURES"
      },
      "authority_scope":"NON_ENGINEERING_REFERENCE_ONLY",
      "authority_transfer":False,
      "formal_credit_delta":0,
      "engineering_promotion_forbidden":True,
      "abacus_bridge_compensation_forbidden":True
    }
    Path(args.receipt).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")

if __name__=="__main__":
    main()
