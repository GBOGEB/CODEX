#!/usr/bin/env bash
set -euo pipefail
ROOT="$(git rev-parse --show-toplevel)"; cd "$ROOT"; mkdir -p .preflight
python - <<'PY'
from pathlib import Path
import json, subprocess, hashlib, sys
checks=[]
def run(name, cmd):
 p=subprocess.run(cmd,shell=True,text=True,capture_output=True); checks.append({'name':name,'status':'PASS' if p.returncode==0 else 'FAIL','returncode':p.returncode});
 if p.returncode: sys.stderr.write(p.stdout+p.stderr)
 return p.returncode
rc=run('python_compile',"python -m compileall -q . -x '(^|/)(\.git|\.venv|venv|node_modules)/'")
for name,cmd,path in [
 ('ssot_validator','python tools/validators/ssot_validator.py','tools/validators/ssot_validator.py'),
 ('master_input_validator','python tools/validators/master_input_validator.py','tools/validators/master_input_validator.py'),
 ('dependency_trace','python tools/traceability/dependency_engine.py','tools/traceability/dependency_engine.py'),
 ('lineage','python tools/traceability/lineage_engine.py','tools/traceability/lineage_engine.py')]:
 if Path(path).exists(): rc |= run(name,cmd)
tracked=subprocess.check_output(['git','ls-files'],text=True).splitlines(); h=hashlib.sha256()
for name in sorted(tracked):
 p=Path(name)
 if p.is_file(): h.update(name.encode()); h.update(b'\0'); h.update(p.read_bytes()); h.update(b'\0')
receipt={'schema':'cross_repo_preflight/v0.1','repo':subprocess.check_output(['git','config','--get','remote.origin.url'],text=True).strip(),'head_sha':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'tracked_tree_content_sha256':h.hexdigest(),'checks':checks,'status':'PASS' if rc==0 else 'FAIL','authority':'advisory_preflight_not_governed_evidence'}
Path('.preflight/receipt.json').write_text(json.dumps(receipt,indent=2)+'\n'); print(json.dumps(receipt,indent=2)); sys.exit(1 if rc else 0)
PY
