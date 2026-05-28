#!/usr/bin/env python3
import hashlib, json
from pathlib import Path
r=Path(__file__).resolve().parents[1]
files=[r/'build'/'semantic_ast.json',r/'build'/'semantic_ir.json',r/'build'/'render_graph.json',r/'build'/'lineage_graph.json',r/'build'/'execution_graph.json',r/'build'/'reconciliation_state.json',r/'build'/'mutation_profile.json',r/'telemetry'/'telemetry_runtime.json',r/'dist'/'index.html']
manifest=[]
for p in files:
    b=p.read_bytes(); manifest.append({"path":str(p.relative_to(r)),"sha256":hashlib.sha256(b).hexdigest()})
(r/'dist').mkdir(exist_ok=True)
json.dump({"artifacts_signed":len(manifest),"files":manifest}, (r/'dist'/'manifest.json').open('w'), indent=2)
print('manifest written')
