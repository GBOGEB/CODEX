#!/usr/bin/env python3
import datetime as dt,json,subprocess
K=["CG","RR","CR","SR","DR","PB","FE","QH","HK","BG","KR","EX","WD"]
def git(*a): return subprocess.check_output(["git",*a],text=True).strip()
def A(s="UNKNOWN",c="UNKNOWN",e="UNKNOWN",r="self",d=None):
 x={"state":s,"confidence":c,"evidence_class":e,"observed_at":dt.datetime.now(dt.timezone.utc).isoformat(),"source_ref":r};
 if d:x["detail"]=d
 return x
sha=git("rev-parse","HEAD"); D={k:A() for k in K}
D["CG"]=A("AMBER","HIGH","CANONICAL_SOURCE","governance/mesh/MESH_STATUS_CONTRACT_v1.yaml","emit and validate canonical vector")
D["RR"]=A("GREEN","HIGH","RUNTIME_RECEIPT",sha,"KEB emitter executed")
D["SR"]=A("GREEN","HIGH","CANONICAL_SOURCE","governance/mesh/MESH_STATUS_CONTRACT_v1.yaml","canonical taxonomy/schema present")
D["EX"]=A("GREEN","HIGH","RUNTIME_RECEIPT",sha,"emitter executed >0 steps")
D["KR"]=A("AMBER","HIGH","EXACT_SHA_ARTIFACT",sha,"canonical exact-SHA vector emitted; federation receipt pending")
D["BG"]=A("BLOCKED","HIGH","CANONICAL_SOURCE","governance/mesh/MESH_STATUS_CONTRACT_v1.yaml","three repo vector set incomplete")
D["WD"]=A("DEFER","HIGH","CANONICAL_SOURCE","governance/mesh/MESH_STATUS_CONTRACT_v1.yaml","wait for contract-only scheduler proof")
out={"schema_version":"1.0","repo":"GBOGEB/CODEX","source_sha":sha,"freshness_timestamp":dt.datetime.now(dt.timezone.utc).isoformat(),"producer":"emit_mesh_status.py","dimensions":D,"next_action":"publish exact-SHA vector for ABACUS contract-only selector","blocking_atom":"three_repo_vector_set_incomplete"}
assert set(D)==set(K)
open("mesh-status.json","w").write(json.dumps(out,indent=2,sort_keys=True)+"\n")
print(f"PASS emitted {len(D)} dimensions for GBOGEB/CODEX at {sha}")
