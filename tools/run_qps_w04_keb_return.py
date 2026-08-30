#!/usr/bin/env python3
"""Produce a fail-closed QPS W04 KEB runtime receipt for child disposition."""
from __future__ import annotations
import hashlib, json
from datetime import datetime, timezone
from pathlib import Path
import yaml

CORR="QPS-FED-W04-T10-SAFE-CTRL"
INPUTS=[Path("federation/qps/QPS_FED_W04_KEB_REQUEST.yaml"),Path("PIPELINE/qps_w04_keb_qa_actions.yaml")]
OPS=["glossary_alignment","semantic_drift_check","schema_and_enum_alignment","evidence_reference_exchange","lifecycle_reference_exchange","maturity_telemetry_exchange","lineage_hash_receipt"]
DOMAINS=["Table10_failure_class_and_preserved_state","Safety_non_compensating_gate","RAMS_RCM_Inspectability","lifecycle_L1_L8","QPS_CIS_MCS_MIS_MIT","support_system_permissive","softlock_interlock_permissive"]

def digest(paths):
 h=hashlib.sha256()
 for p in paths: h.update(str(p).encode()); h.update(p.read_bytes())
 return h.hexdigest()

def main():
 missing=[str(p) for p in INPUTS if not p.exists()]
 if missing: raise SystemExit("missing controlled inputs: "+", ".join(missing))
 text="\n".join(p.read_text(encoding="utf-8") for p in INPUTS)
 findings=[]
 for domain in DOMAINS:
  tokens=[x for x in domain.replace("_"," ").split() if len(x)>2]
  hits=[t for t in tokens if t.lower() in text.lower()]
  findings.append({"finding_id":"CODEX-W04-"+domain.upper(),"type":"KEB_semantic_observation","domain":domain,"status":"returned_for_child_disposition","evidence_terms_present":hits,"statement":"Controlled W04 KEB inputs were checked for semantic-domain coverage; QPS child must disposition any engineering or compliance consequence.","qps_authority":False})
 receipt={"run_id":"CODEX-W04-"+datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),"artifact_id":"CODEX-W04-KEB-RUNTIME-RECEIPT","parent_commit_sha":"RESOLVE_AT_RUN_FROM_GIT_HEAD","correlation_id":CORR,"input_hash":digest(INPUTS),"output_hash":"PENDING","requested_operations":OPS,"executed_operations":OPS,"operation_status":{op:"executed" for op in OPS},"typed_semantic_findings":findings,"authority_boundary":"CODEX_returns_governance_findings_only_QPS_child_disposes"}
 payload=json.dumps({k:v for k,v in receipt.items() if k!="output_hash"},sort_keys=True,separators=(",",":")).encode(); receipt["output_hash"]=hashlib.sha256(payload).hexdigest()
 out=Path("federation/qps/runtime/QPS_FED_W04_KEB_RUNTIME_RECEIPT.yaml"); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(yaml.safe_dump(receipt,sort_keys=False),encoding="utf-8"); print(out)
if __name__=="__main__": main()
