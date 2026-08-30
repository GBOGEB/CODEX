#!/usr/bin/env python3
"""Validate fixture-wrapped or root W04 KEB receipts."""
from __future__ import annotations
import hashlib,json,re,sys
from pathlib import Path
from typing import Any
import yaml
CORR="QPS-FED-W04-T10-SAFE-CTRL"; DOMAINS={"Table10_failure_class_and_preserved_state","Safety_non_compensating_gate","RAMS_RCM_Inspectability","lifecycle_L1_L8","QPS_CIS_MCS_MIS_MIT","support_system_permissive","softlock_interlock_permissive"}
REQUIRED={"run_id","artifact_id","parent_repository","parent_commit_sha","child_source_ref","correlation_id","input_hash","glossary_hash","output_hash","requested_operations","executed_operations","operation_status","typed_semantic_findings","semantic_domains_for_regression","child_disposition_placeholder","authority_boundary"}
def load(path:Path)->dict[str,Any]:
 data=yaml.safe_load(path.read_text(encoding="utf-8"));
 if not isinstance(data,dict): raise ValueError("receipt must be a YAML mapping")
 return data
def validate(data:dict[str,Any])->list[str]:
 errors=[]; wrapped="example_valid_receipt" in data; receipt=data.get("example_valid_receipt") if wrapped else data
 if not isinstance(receipt,dict): return ["receipt missing or not a mapping"]
 if receipt.get("correlation_id")!=CORR: errors.append("correlation_id mismatch")
 if "QPS_child_disposes" not in str(receipt.get("authority_boundary","")): errors.append("child authority boundary missing")
 if receipt.get("requested_operations")!=receipt.get("executed_operations"): errors.append("requested/executed operation mismatch")
 if wrapped:
  domains=data.get("semantic_domains_for_regression",[])
  if not DOMAINS.issubset(set(domains)): errors.append("fixture semantic domains incomplete")
  return errors
 missing=sorted(REQUIRED-set(receipt))
 if missing: errors.append("missing runtime fields: "+", ".join(missing))
 if not re.fullmatch(r"[0-9a-f]{40}",str(receipt.get("parent_commit_sha",""))): errors.append("parent_commit_sha must be resolved")
 if not DOMAINS.issubset(set(receipt.get("semantic_domains_for_regression",[]))): errors.append("semantic regression domains incomplete")
 status=receipt.get("operation_status")
 if not isinstance(status,dict): errors.append("operation_status must be a mapping")
 else:
  for op in receipt.get("executed_operations",[]):
   row=status.get(op)
   if not isinstance(row,dict) or row.get("executed") is not True or row.get("status")!="PASS" or not row.get("mechanic_path"): errors.append(f"operation {op} lacks executed PASS mechanic")
 payload=json.dumps({k:v for k,v in receipt.items() if k!="output_hash"},sort_keys=True,separators=(",",":")).encode()
 if hashlib.sha256(payload).hexdigest()!=receipt.get("output_hash"): errors.append("output_hash mismatch")
 return errors
def main(argv:list[str])->int:
 path=Path(argv[1]) if len(argv)>1 else Path("tests/fixtures/qps_w04_keb_receipt_fixture.yaml"); errors=validate(load(path))
 for error in errors: print("ERROR: "+error,file=sys.stderr)
 if not errors: print(f"OK: {path} satisfies QPS W04 KEB receipt contract")
 return 1 if errors else 0
if __name__=="__main__": raise SystemExit(main(sys.argv))
