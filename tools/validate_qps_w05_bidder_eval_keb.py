#!/usr/bin/env python3
from __future__ import annotations
import argparse
from pathlib import Path
import yaml

REQUIRED={"run_id","artifact_id","parent_repository","parent_commit_sha","correlation_id","source_child_merge_sha","input_hash","snapshot_hash","glossary_hash","output_hash","requested_operations","executed_operations","operation_status","typed_semantic_findings","child_disposition_placeholder","authority_boundary"}

def main()->int:
    p=argparse.ArgumentParser(); p.add_argument("receipt"); a=p.parse_args()
    data=yaml.safe_load(Path(a.receipt).read_text(encoding="utf-8"))
    if not isinstance(data,dict): raise SystemExit("receipt is not a mapping")
    missing=sorted(REQUIRED-set(data))
    if missing: raise SystemExit(f"missing fields: {missing}")
    if data["correlation_id"]!="QPS-FED-W05-BIDDER-EVAL": raise SystemExit("wrong correlation")
    if data["parent_repository"]!="GBOGEB/CODEX": raise SystemExit("wrong parent repository")
    if data["requested_operations"]!=data["executed_operations"]: raise SystemExit("operation mismatch")
    if data["child_disposition_placeholder"]!="UNSET": raise SystemExit("parent self-disposition prohibited")
    if not data["typed_semantic_findings"]: raise SystemExit("no semantic findings")
    for f in data["typed_semantic_findings"]:
        if f.get("qps_authority") is not False: raise SystemExit("finding claims QPS authority")
        if f.get("disposition_unset") is not True: raise SystemExit("parent disposition must remain unset")
    print("W05 KEB RECEIPT VALIDATION PASSED"); return 0

if __name__=="__main__": raise SystemExit(main())
