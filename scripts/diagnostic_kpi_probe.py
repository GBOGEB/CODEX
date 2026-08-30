#!/usr/bin/env python3
"""Low-impact local KPI probe; intentionally does not create GitHub Actions runs."""
import json,os,subprocess,time,urllib.request
def timed(name,fn):
 t=time.perf_counter();ok=True;err=None
 try:v=fn()
 except Exception as e:ok=False;v=None;err=type(e).__name__
 return {'name':name,'ok':ok,'duration_ms':round((time.perf_counter()-t)*1000,2),'error':err,'value':v}
def cmd(c):
 p=subprocess.run(c,shell=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=120)
 if p.returncode:raise RuntimeError('nonzero')
 return p.returncode
def http():
 with urllib.request.urlopen(os.getenv('MCP_HEALTH_URL','http://127.0.0.1:8765/health'),timeout=2) as r:return r.status
checks=[timed('mcp_health',http)]
if os.path.exists('scripts/preflight.sh'):checks.append(timed('preflight',lambda:cmd('bash scripts/preflight.sh')))
checks += [timed('git_status',lambda:cmd('git status --porcelain')),timed('python_compile',lambda:cmd('python -m compileall -q scripts'))]
print(json.dumps({'schema':'ops-kpi-v1','authority':'operational_non_evidence','checks':checks},sort_keys=True))
