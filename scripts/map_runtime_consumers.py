#!/usr/bin/env python3
"""Map executable census consumers to declared logical IDs and runtime families.

This is diagnostic only: it identifies hard-coded authority paths and potential
runtime competition; it does not consolidate implementations or establish new
authority.
"""
from __future__ import annotations
import json, re
from collections import Counter, defaultdict
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[1]
BOUND=ROOT/'reports/codex_2_0_ssot_bound_census.json'; REG=ROOT/'ssot/registry/authority_registry.yaml'; OUT=ROOT/'reports/codex_2_0_runtime_consumer_map.json'
TEXT_EXT={'.py','.ts','.js','.mjs','.cjs','.yaml','.yml','.json','.md','.toml','.sh'}
RUNTIME_PATTERNS={'MCP_SWEEP':('mcp_sweep','run_mcp_sweep'),'MCP_HEALTH':('mcp_health','MCP_HEALTH_PORT'),'AGENT_ORCHESTRATION':('agentic_orchestration','agent_orchestration'),'FEDERATION_RUNTIME':('federation_runtime','mcp_runtime_directive')}
def main():
    if not BOUND.exists(): raise SystemExit('RUNTIME_MAP_FAIL bound census missing')
    data=json.loads(BOUND.read_text()); rows=data.get('candidates') or []; reg=yaml.safe_load(REG.read_text()) or {}; nodes=reg.get('nodes') or {}
    declared={lid:n.get('path') for lid,n in nodes.items() if isinstance(n,dict) and n.get('path')}
    consumers=[]; families=defaultdict(list); hard=Counter(); resolver=Counter()
    for row in rows:
        p=str(row.get('path','')); suffix=Path(p).suffix.lower()
        if suffix not in TEXT_EXT or not (ROOT/p).is_file(): continue
        if row.get('candidate_class')!='CONSUMER_OR_CONTRACT_CANDIDATE' and suffix not in {'.py','.ts','.js','.mjs','.cjs','.sh'}: continue
        try: text=(ROOT/p).read_text(encoding='utf-8',errors='ignore')
        except OSError: continue
        ids=sorted(lid for lid in nodes if re.search(rf'\b{re.escape(str(lid))}\b',text))
        paths=sorted(lid for lid,path in declared.items() if path and str(path) in text)
        for lid in ids: resolver[lid]+=1
        for lid in paths: hard[lid]+=1
        fam=[]
        low=(p+'\n'+text).lower()
        for name,tokens in RUNTIME_PATTERNS.items():
            if any(t.lower() in low for t in tokens): fam.append(name); families[name].append(p)
        if ids or paths or fam: consumers.append({'path':p,'logical_ids':ids,'hard_coded_authority_paths':paths,'runtime_families':fam})
    duplicate={name:sorted(set(paths)) for name,paths in families.items() if len(set(paths))>1}
    result={'consumer_population_from_census':sum(1 for r in rows if r.get('candidate_class')=='CONSUMER_OR_CONTRACT_CANDIDATE'),'mapped_consumers':len(consumers),'logical_id_reference_counts':dict(resolver),'hard_coded_authority_path_counts':dict(hard),'runtime_family_candidate_counts':{k:len(set(v)) for k,v in families.items()},'duplicate_runtime_family_candidates':duplicate,'interpretation':'duplicate family membership is a W04 review candidate, not proof of competing authority','consumers':consumers}
    OUT.write_text(json.dumps(result,indent=2)+'\n')
    print(f"RUNTIME_MAP_PASS census_consumers={result['consumer_population_from_census']} mapped={len(consumers)} duplicate_families={len(duplicate)}")
if __name__=='__main__': main()
