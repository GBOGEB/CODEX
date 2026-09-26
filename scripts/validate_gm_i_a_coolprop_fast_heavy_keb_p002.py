#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
from ruamel.yaml import YAML

ROOT=Path(__file__).resolve().parents[1]
BRIDGE=ROOT/"triage/GM_I_A_COOLPROP_FAST_HEAVY_KEB_BRIDGE_P002.yaml"
EXPECTED_DIGEST="af1115346ff212addbcaa855faa5f65e8989a0de01742decb6ba30e16a60affa"
EXPECTED_SOURCE="a88d6e8cc24402868afab39a71fc49fcacec08c8"
EXPECTED_MERGE="e31433c4427be2aaad064294e6c6cab1843537df"
EXPECTED_RUN=36226071145

def require(c,m):
    if not c: raise ValueError(m)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--provider",required=True); ap.add_argument("--receipt",required=True); args=ap.parse_args()
    bridge=YAML(typ="safe").load(BRIDGE.read_text(encoding="utf-8")) or {}
    require(bridge.get("pulse_id")=="GM-I-A-MCLOCK-P002","pulse mismatch")
    raw=Path(args.provider).read_bytes()
    digest=hashlib.sha256(raw).hexdigest()
    require(digest==EXPECTED_DIGEST,"provider digest mismatch")
    d=json.loads(raw)
    require(d.get("pulse_id")=="GM-I-A-MCLOCK-P002","provider pulse mismatch")
    require(d.get("source_head_sha")==EXPECTED_SOURCE,"source mismatch")
    require(d.get("source_merge_sha")==EXPECTED_MERGE,"merge mismatch")
    require((d.get("workflow") or {}).get("run_id")==EXPECTED_RUN,"run mismatch")
    require((d.get("workflow") or {}).get("conclusion")=="success","workflow not success")
    require((d.get("heavy") or {}).get("conclusion")=="success","heavy not success")
    require((d.get("fast") or {}).get("conclusion")=="success","fast not success")
    require((d.get("fast") or {}).get("build_invoked") is False,"fast rebuilt")
    require((d.get("fast") or {}).get("source_checkout_performed") is False,"fast checkout")
    require((d.get("authority") or {}).get("authority_transfer") is False,"authority transfer")
    out={
      "schema":"codex.keb.gm_i_a.fast_heavy.v1",
      "pulse_id":"GM-I-A-MCLOCK-P002",
      "status":"PASS_VALIDATED_CANDIDATE",
      "promotion_state":"NON_ENGINEERING_REFERENCE_ONLY",
      "canonical_keb_atom":False,
      "provider_repo":"GBOGEB/CoolProp",
      "provider_attestation_commit":"0873f07f9bc1e5eb9fdbdd3219c826d97eb148dc",
      "provider_attestation_sha256":digest,
      "provider_source_head_sha":d["source_head_sha"],
      "provider_runtime_run_id":d["workflow"]["run_id"],
      "knowledge":{
        "heavy_build_seconds":d["heavy"]["build_seconds"],
        "heavy_queue_seconds":d["heavy"]["queue_seconds"],
        "fast_execute_seconds":d["fast"]["execute_seconds"],
        "fast_queue_seconds":d["fast"]["queue_seconds"],
        "observation":"P002_REPEAT_SEPARATES_QUEUE_VARIANCE_FROM_STABLE_EXECUTION"
      },
      "authority_scope":"NON_ENGINEERING_REFERENCE_ONLY",
      "authority_transfer":False,
      "formal_credit_delta":0,
      "engineering_promotion_forbidden":True,
      "abacus_bridge_compensation_forbidden":True
    }
    Path(args.receipt).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
if __name__=="__main__": main()
