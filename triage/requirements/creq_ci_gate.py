#!/usr/bin/env python3
import argparse,hashlib,json,subprocess,sys
from datetime import date
from pathlib import Path
EXPECTED="541fbff68b298427ae8fc560efede6348ed7a8a27712b9e3c762225eb2de2eaa"; ROLES={"local_repo_owner","parent_cADR_or_cOCD_authority","global_CReq_authority"}
def load(p): return json.loads(Path(p).read_text())
def fail(m): print("CReq federation CI: FAIL - "+m); raise SystemExit(1)
def main():
 p=argparse.ArgumentParser(); p.add_argument("--registry",required=True); p.add_argument("--overlay",required=True); p.add_argument("--resolver",required=True); p.add_argument("--out",required=True); a=p.parse_args(); root=Path.cwd(); raw=Path(a.registry).read_bytes(); digest=hashlib.sha256(raw).hexdigest()
 if digest!=EXPECTED: fail("registry digest drift: "+digest)
 reg=load(a.registry); ov=load(a.overlay); gs={x["id"] for x in reg["requirements"]}; prefix="CReq_CODEX_"
 for x in ov.get("requirements",[]):
  if not x["id"].startswith(prefix): fail(x["id"]+": namespace shadowing")
  parent=x.get("overrides") or x.get("parent_global_requirement")
  if parent not in gs: fail(x["id"]+": unknown global parent")
  if x.get("mode","addition")=="override" and x.get("approval_state")=="APPROVED":
   rp=x.get("approval_receipt")
   if not rp or not (root/rp).exists(): fail(x["id"]+": missing approval receipt")
   r=load(root/rp); roles={z.get("role") for z in r.get("approval_chain",[]) if z.get("state")=="APPROVED"}
   if not ROLES.issubset(roles): fail(x["id"]+": approval roles incomplete")
   exp=r.get("expires_at")
   if exp and date.fromisoformat(exp[:10])<date.today(): fail(x["id"]+": approval expired")
 out=Path(a.out); out.parent.mkdir(parents=True,exist_ok=True); subprocess.run([sys.executable,a.resolver,"--global-registry",a.registry,"--overlay",a.overlay,"--out",a.out],check=True); rr=load(out); ids={r["effective_id"] for r in rr["effective_requirements"]}
 for x in ov.get("requirements",[]):
  mode=x.get("mode","addition"); parent=x.get("overrides") or x.get("parent_global_requirement"); approved=mode=="override" and x.get("approval_state")=="APPROVED"
  if mode=="addition" and not ({x["id"],parent}<=ids): fail(x["id"]+": addition precedence divergence")
  if mode=="override" and approved and (x["id"] not in ids or parent in ids): fail(x["id"]+": approved override precedence divergence")
  if mode=="override" and not approved and (parent not in ids or x["id"] in ids): fail(x["id"]+": fallback precedence divergence")
 gate={"status":"PASS","repo":ov["repo"],"global_registry_sha256":digest,"global_count":len(gs),"effective_count":len(ids),"checks":["registry_digest","namespace_shadowing","approval_validity","approval_expiry","resolver_execution","precedence"]}; Path(str(out).replace("RESOLUTION","GATE")).write_text(json.dumps(gate,indent=2)+"\n"); print("CReq federation CI: PASS")
if __name__=="__main__": main()
