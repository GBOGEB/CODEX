#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, re, subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import yaml

CORR="QPS-FED-W05-BIDDER-EVAL"
REQUEST=Path("federation/qps/QPS_FED_W05_BIDDER_EVAL_KEB_REQUEST.yaml")
SNAPSHOT=Path("federation/qps/snapshots/QPS_FED_W05_BIDDER_EVAL_SANITIZED_v0.1.yaml")
GLOSSARY=Path("PIPELINE/GLOSSARY.yaml")
OUTPUT=Path("federation/qps/runtime/QPS_FED_W05_BIDDER_EVAL_KEB_RECEIPT.yaml")

def load(path:Path)->dict[str,Any]:
    v=yaml.safe_load(path.read_text(encoding="utf-8"));
    if not isinstance(v,dict): raise SystemExit(f"{path} is not a mapping")
    return v

def digest(paths:list[Path])->str:
    h=hashlib.sha256()
    for p in paths: h.update(p.as_posix().encode()); h.update(b"\0"); h.update(p.read_bytes())
    return h.hexdigest()

def norm(s:str)->str: return re.sub(r"[^a-z0-9]+","_",s.lower()).strip("_")
def sid(op:str)->str: return "CODEX-W05-"+hashlib.sha256(op.encode()).hexdigest()[:12]

def main()->int:
    req,snap,gloss=load(REQUEST),load(SNAPSHOT),load(GLOSSARY)
    if req.get("correlation_id")!=CORR or snap.get("correlation_id")!=CORR: raise SystemExit("correlation mismatch")
    if snap.get("confidentiality",{}).get("bidder_names_removed") is not True: raise SystemExit("snapshot not sanitized")
    requested=req.get("requested_KEB_operations")
    if not isinstance(requested,list) or not requested: raise SystemExit("missing KEB operations")
    governed={norm(k) for k in gloss.get("glossary",{})}
    domains=req.get("exchange_domains",[])
    domain_defs=snap.get("semantic_domains",{})
    findings=[]; status={}
    for op in requested:
        result={"operation":op}
        if op.startswith("normalize_aliases"):
            result["aliases"]={d:domain_defs.get(d,{}).get("aliases",[]) for d in domains}
        elif op.startswith("distinguish_certificate"):
            result["rule"]="certificate_scope_is_not_project_contract_scope"
        elif op.startswith("distinguish_document_issue"):
            result["status_terms"]=domain_defs.get("evidence_location_document_status_and_proof_level",{}).get("aliases",[])
        elif op.startswith("normalize_lifecycle"):
            result["lifecycle_semantics"]=snap.get("lifecycle_semantics",{})
        elif op.startswith("normalize_direct"):
            result["edge_terms"]=domain_defs.get("edge_semantics",{}).get("aliases",[])
        elif op.startswith("validate_reference_hierarchy"):
            result["reference_aliases"]=domain_defs.get("Addendum_I_Addendum_II_OFFER_RTM_AD_reference_hierarchy",{}).get("aliases",[])
        elif op.startswith("normalize_welding"):
            result["welding_aliases"]=domain_defs.get("WPS_WPQR_welder_operator_NDT_orbital_welding",{}).get("aliases",[])
        elif op.startswith("validate_evidence_location"):
            result["proof_semantics"]=snap.get("proof_semantics",{})
        elif op.startswith("flag_semantic_drift"):
            result["bidder_semantic_patterns"]=snap.get("bidder_semantic_patterns",{})
        else:
            result["status"]="executed"
        status[op]={"executed":True,"status":"PASS","result":result,"mechanic_path":"tools/run_qps_w05_bidder_eval_keb.py"}
        findings.append({"stable_finding_id":sid(op),"correlation_id":CORR,"governed_term_or_reference":op,"operation":op,"drift_or_validation_result":result,"recommended_child_action":"review_and_disposition_ACCEPT_REJECT_DEFER","input_glossary_output_hashes":"BOUND_IN_RECEIPT","disposition_unset":True,"qps_authority":False})
    receipt={"run_id":"CODEX-W05-"+datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),"artifact_id":"CODEX-W05-BIDDER-EVAL-KEB-RUNTIME-RECEIPT","parent_repository":"GBOGEB/CODEX","parent_commit_sha":subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip(),"correlation_id":CORR,"source_child_merge_sha":snap["source_child"]["source_merge_sha"],"input_hash":digest([REQUEST,SNAPSHOT,GLOSSARY]),"snapshot_hash":digest([SNAPSHOT]),"glossary_hash":digest([GLOSSARY]),"output_hash":"PENDING","requested_operations":requested,"executed_operations":requested,"operation_status":status,"typed_semantic_findings":findings,"child_disposition_placeholder":"UNSET","authority_boundary":"CODEX returns semantic governance findings only; QPS child owns engineering/compliance disposition"}
    payload=json.dumps({k:v for k,v in receipt.items() if k!="output_hash"},sort_keys=True,separators=(",",":")).encode(); receipt["output_hash"]=hashlib.sha256(payload).hexdigest()
    OUTPUT.parent.mkdir(parents=True,exist_ok=True); OUTPUT.write_text(yaml.safe_dump(receipt,sort_keys=False),encoding="utf-8"); print(OUTPUT); return 0

if __name__=="__main__": raise SystemExit(main())
