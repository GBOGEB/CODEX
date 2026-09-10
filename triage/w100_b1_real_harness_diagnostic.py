#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path

CHILD_SHA='a00785568f617db729a3968127d258027b5daa33'
EXPECTED={
 'canonical':('QPS_OFFER_Cluster_v3_4_BT_RTM_Standards_Evidence.xlsx','00a5f0ed3ded00620a33edd045706ba5fb9a67b5fb7fe63c495305f911c43ccb'),
 'alat':('QPS_ALAT_SSOT_CURRENT_2026-09-07.xlsx','5c4c845f7e9d88c1bfe002817c98e5584135cc8bc85bf9ea6596c183318a1907'),
 'lkt_w42':('QPS_LKT_NEG_RFI_REVIEW_MASTER_W21_2.xlsx','6d763cce948a1ee14c30c42b0367226f97dc4712beb6ab4b6e641ad0e8b00f3f'),
 'w22l':('QPS_LKT_ALAT_RTM_COMPLIANCE_W22L_RETURN_PACKAGES.xlsx','b745ef62417d921495bffdc3154e8fc0340216d4ba7ad85e847a0b468a5327e4'),
}
def sha256(p:Path):
 h=hashlib.sha256();
 with p.open('rb') as f:
  for c in iter(lambda:f.read(1024*1024),b''): h.update(c)
 return h.hexdigest()
def main():
 root=Path('.')
 obs={}; ok=True
 for key,(name,expected) in EXPECTED.items():
  ms=[p for p in root.rglob(name) if p.is_file()]
  actual=None
  if len(ms)==1:
   actual=sha256(ms[0]); state='PASS' if actual==expected else 'HASH_MISMATCH'
  elif len(ms)>1: state='AMBIGUOUS'
  else: state='MISSING'
  ok &= state=='PASS'; obs[key]={'filename':name,'expected_sha256':expected,'actual_sha256':actual,'state':state}
 out={'schema':'w100-b1-diagnostic/v1','source_repository':'GBOGEB/cryoplant-project','source_pr':820,'source_head_sha':CHILD_SHA,'authority':'diagnostic_only','governed_inputs':obs,'status':'PASS_INPUT_GATE' if ok else 'DEFER_GOVERNED_INPUT_MISSING_OR_INVALID','engineering_delta':0,'negotiation_delta':0,'release_delta':0}
 Path('out').mkdir(exist_ok=True); Path('out/W100_B1_DIAGNOSTIC_RECEIPT.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
 print(json.dumps(out,sort_keys=True)); return 0 if ok else 3
if __name__=='__main__': raise SystemExit(main())
