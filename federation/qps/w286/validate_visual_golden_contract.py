#!/usr/bin/env python3
import argparse, json, re
from pathlib import Path
HEX64=re.compile(r"^[0-9a-f]{64}$")
VARIANTS=["A_dark_exec","B_dense_matrix","C_landscape_appendix","D_cards_dashboard","E_plain_contract"]
FORMATS=["html","docx","pdf","pptx","xlsx"]

def validate(d):
    e=[]
    if d.get("schema")!="qps-visual-golden-sanitized/1.0": e.append("schema")
    if d.get("variants")!=VARIANTS: e.append("variants")
    if d.get("required_formats")!=FORMATS: e.append("formats")
    if d.get("sample_only") is not True: e.append("sample_only")
    if d.get("visual_binary_hashes_pairwise_distinct") is not True: e.append("binary_divergence")
    if d.get("representative_render_hashes_pairwise_distinct") is not True: e.append("render_divergence")
    if d.get("semantic_authority")!="EXTERNAL_CHILD_QPS_ONLY": e.append("authority_inversion")
    if d.get("contains_qps_engineering_content") is not False: e.append("content_leak")
    if d.get("formal_credit_delta")!=0: e.append("formal_credit")
    if not HEX64.match(str(d.get("corpus_zip_sha256",""))): e.append("zip_hash")
    return e

def main():
    p=argparse.ArgumentParser(); p.add_argument("path",type=Path); a=p.parse_args()
    d=json.loads(a.path.read_text(encoding="utf-8")); e=validate(d)
    print(json.dumps({"passed":not e,"errors":e},sort_keys=True)); return 0 if not e else 2
if __name__=="__main__": raise SystemExit(main())
