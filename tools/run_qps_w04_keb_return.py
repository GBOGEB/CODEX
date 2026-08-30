#!/usr/bin/env python3
"""Produce a source-bound, fail-closed QPS W04 KEB runtime receipt."""
from __future__ import annotations
import argparse, hashlib, json, re, subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import yaml

CORR="QPS-FED-W04-T10-SAFE-CTRL"; REQUEST=Path("federation/qps/QPS_FED_W04_KEB_REQUEST.yaml"); QA=Path("PIPELINE/qps_w04_keb_qa_actions.yaml"); GLOSSARY=Path("PIPELINE/GLOSSARY.yaml")

def load(path: Path) -> dict[str, Any]:
 value=yaml.safe_load(path.read_text(encoding="utf-8"))
 if not isinstance(value,dict): raise SystemExit(f"{path} is not a YAML mapping")
 return value
def digest(paths: list[Path]) -> str:
 h=hashlib.sha256()
 for path in paths: h.update(path.as_posix().encode()); h.update(b"\0"); h.update(path.read_bytes())
 return h.hexdigest()
def git_sha() -> str:
 value=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip()
 if not re.fullmatch(r"[0-9a-f]{40}",value): raise SystemExit("unable to resolve parent git SHA")
 return value
def norm(value: str) -> str: return re.sub(r"[^a-z0-9]+","_",value.lower()).strip("_")

def main() -> int:
 parser=argparse.ArgumentParser(); parser.add_argument("--child-root",required=True); parser.add_argument("--child-sha",required=True); parser.add_argument("--output",default="federation/qps/runtime/QPS_FED_W04_KEB_RUNTIME_RECEIPT.yaml"); args=parser.parse_args()
 if not re.fullmatch(r"[0-9a-f]{40}",args.child_sha): raise SystemExit("--child-sha must be a full commit SHA")
 request,qa,glossary=load(REQUEST),load(QA),load(GLOSSARY)
 requested=request.get("requested_KEB_operations")
 supported={"glossary_alignment","semantic_drift_check","schema_and_enum_alignment","ADR_index_exchange","evidence_reference_exchange","lifecycle_and_standard_reference_exchange","maturity_telemetry_exchange","lineage_hash_receipt"}
 if not isinstance(requested,list) or set(requested)!=supported: raise SystemExit("controlled request operations do not match implemented mechanics")
 child_root=Path(args.child_root); evidence=list(child_root.rglob("QPS_TABLE10_SUPPORT_SYSTEM_COMPANION_v0.1.yaml"))+list(child_root.rglob("QPS_SAFETY_EVIDENCE_RTM_OFFER_CROSSWALK_v0.1.yaml"))
 if len(evidence)!=2: raise SystemExit(f"expected two controlled child artifacts; found {len(evidence)}")
 inputs=[REQUEST,QA,GLOSSARY,*evidence]; corpus="\n".join(p.read_text(encoding="utf-8") for p in evidence); governed={norm(k) for k in glossary.get("glossary",{})}; domains=request.get("exchange_domains",[])
 status={}; findings=[]
 for operation in requested:
  result: dict[str,Any]={"operation":operation}
  if operation=="glossary_alignment": result["ungoverned_terms"]=[d for d in domains if norm(d) not in governed]
  elif operation=="semantic_drift_check": result["case_or_separator_variants"]=[d for d in domains if d not in corpus and norm(d) in norm(corpus)]
  elif operation=="schema_and_enum_alignment": result["domains_present"]=[d for d in domains if norm(d) in norm(corpus)]
  elif operation=="ADR_index_exchange": result["ADR_references"]=sorted(set(re.findall(r"ADR[-_A-Za-z0-9.]+",corpus)))
  elif operation=="evidence_reference_exchange": result["evidence_references"]=[{"path":p.as_posix(),"sha256":digest([p])} for p in evidence]
  elif operation=="lifecycle_and_standard_reference_exchange": result["lifecycle_terms"]=sorted(set(re.findall(r"\bL[1-8](?:_[A-Z]+)?\b",corpus))); result["standard_references"]=sorted(set(re.findall(r"\b(?:EN|ISO|IEC)\s*[-:]?\s*\d+[A-Za-z0-9:-]*",corpus)))
  elif operation=="maturity_telemetry_exchange": result["open_markers"]={m:corpus.lower().count(m) for m in ("tbd","partial","not_assessed","open")}
  elif operation=="lineage_hash_receipt": result["input_hash"]=digest(inputs)
  status[operation]={"executed":True,"status":"PASS","mechanic_path":"tools/run_qps_w04_keb_return.py::"+operation,"result":result}
  if operation in {"glossary_alignment","semantic_drift_check","schema_and_enum_alignment","lifecycle_and_standard_reference_exchange"}: findings.append({"finding_id":"CODEX-W04-"+hashlib.sha256(operation.encode()).hexdigest()[:12],"finding_type":"KEB_semantic_observation","operation":operation,"governed_result":result,"evidence_reference":[p.as_posix() for p in evidence],"recommended_child_action":"review_and_disposition_governance_observation","qps_authority":False})
 receipt={"run_id":"CODEX-W04-"+datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),"artifact_id":"CODEX-W04-KEB-RUNTIME-RECEIPT","parent_repository":"GBOGEB/CODEX","parent_commit_sha":git_sha(),"child_source_ref":f"GBOGEB/cryoplant-project@{args.child_sha}","correlation_id":CORR,"input_hash":digest(inputs),"glossary_hash":digest([GLOSSARY]),"output_hash":"PENDING","requested_operations":requested,"executed_operations":requested,"operation_status":status,"typed_semantic_findings":findings,"semantic_domains_for_regression":["Table10_failure_class_and_preserved_state","Safety_non_compensating_gate","RAMS_RCM_Inspectability","lifecycle_L1_L8","QPS_CIS_MCS_MIS_MIT","support_system_permissive","softlock_interlock_permissive"],"child_disposition_placeholder":"UNSET","authority_boundary":"CODEX_returns_governance_findings_only_QPS_child_disposes"}
 payload=json.dumps({k:v for k,v in receipt.items() if k!="output_hash"},sort_keys=True,separators=(",",":")).encode(); receipt["output_hash"]=hashlib.sha256(payload).hexdigest()
 out=Path(args.output); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(yaml.safe_dump(receipt,sort_keys=False),encoding="utf-8"); print(out); return 0
if __name__=="__main__": raise SystemExit(main())
