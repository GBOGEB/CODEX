#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re
from pathlib import Path
REF_RE=re.compile(r"^(.*?)(\d+)$")
REQUIRED_VIEWS={"executive","minutes","engineering","html_super"}

def compact(values):
    out=[]; parts=[]; run=[]; fam=None; last=None
    def flush_run():
        nonlocal run
        if run:
            parts.append(run[0][0] if len(run)==1 else f"{run[0][0]}..{run[-1][2]:0{run[-1][3]}d}")
            run=[]
    def flush_fam():
        nonlocal parts,fam,last
        flush_run()
        if parts: out.append(", ".join(parts))
        parts=[]; fam=None; last=None
    for raw in [str(x).strip() for x in values if str(x).strip()]:
        m=REF_RE.match(raw)
        if not m:
            flush_fam(); out.append(raw); continue
        prefix,digits=m.group(1),m.group(2); f=(prefix,len(digits)); n=int(digits)
        if fam is not None and f!=fam: flush_fam()
        if fam is None: fam=f
        if run and last is not None and n==last+1: run.append((raw,prefix,n,len(digits)))
        else: flush_run(); run=[(raw,prefix,n,len(digits))]
        last=n
    flush_fam(); return "; ".join(out)

def validate(data):
    errors=[]
    if data.get("schema")!="qps-human-rendition-sanitized/1.0": errors.append("schema")
    refs=data.get("atomic_refs") or []
    if not refs: errors.append("atomic_refs_empty")
    if data.get("rendered_refs")!=compact(refs): errors.append("reference_parity")
    if set(data.get("views") or [])!=REQUIRED_VIEWS: errors.append("view_contract")
    if data.get("authority")!="CHILD_QPS_ENGINEERING_AUTHORITY_EXTERNAL": errors.append("authority_inversion")
    if data.get("contains_bidder_text") is not False: errors.append("bidder_text_leak")
    if data.get("contains_bidder_identity") is not False: errors.append("bidder_identity_leak")
    if data.get("formal_credit_delta")!=0: errors.append("formal_credit")
    if data.get("source_gap_visible") is not True: errors.append("source_gap_hidden")
    return errors

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("path",type=Path); args=ap.parse_args()
    data=json.loads(args.path.read_text(encoding="utf-8")); errors=validate(data)
    print(json.dumps({"passed":not errors,"errors":errors,"rendered_refs":compact(data.get("atomic_refs") or [])},indent=2,sort_keys=True))
    return 0 if not errors else 2
if __name__=="__main__": raise SystemExit(main())
