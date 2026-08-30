#!/usr/bin/env python3
"""Local T0 diagnostics. Never dispatches GitHub Actions; operational metrics only."""
import glob,hashlib,json,os,shutil,subprocess,time
def probe(name,cmd=None,fn=None):
 t=time.perf_counter();status='ok';detail=None
 try:
  if fn:detail=fn()
  else:
   p=subprocess.run(cmd,shell=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=180)
   if p.returncode:status='failed';detail={'returncode':p.returncode}
 except Exception as e:status='failed';detail={'error':type(e).__name__}
 return {'name':name,'status':status,'duration_ms':round((time.perf_counter()-t)*1000,2),'detail':detail}
def skip(n,w):return {'name':n,'status':'skipped','duration_ms':0,'detail':w}
def hash_scan():
 fs=[p for p in glob.glob('**/*',recursive=True) if os.path.isfile(p) and '/.git/' not in '/'+p][:5000];h=hashlib.sha256();total=0
 for p in fs:
  try:b=open(p,'rb').read();h.update(b);total+=len(b)
  except OSError:pass
 return {'files':len(fs),'bytes':total,'sha256':h.hexdigest()}
r=[probe('artifact_hash_scan',fn=hash_scan)]
ys=glob.glob('**/*.yml',recursive=True)+glob.glob('**/*.yaml',recursive=True)
r.append(probe('yaml_parse',cmd="python -c \"import glob,yaml; [yaml.safe_load(open(p,encoding='utf-8')) for p in glob.glob('**/*.y*ml',recursive=True)]\"") if ys else skip('yaml_parse','no yaml'))
r.append(probe('playwright_list',cmd='npx playwright test --list') if shutil.which('npx') and (os.path.exists('playwright.config.js') or os.path.exists('playwright.config.ts')) else skip('playwright_list','playwright config/tool unavailable'))
# KEB contract dry-run: validation/help only, never evidence-producing dispatch.
val=next((p for p in ['scripts/validate_qps_w04_keb_receipt.py','scripts/validate_w04_keb_receipt.py'] if os.path.exists(p)),None)
r.append(probe('keb_contract_dry_run',cmd=f'python {val} --help') if val else skip('keb_contract_dry_run','validator unavailable'))
print(json.dumps({'schema':'ops-kpi-v1','phase':'T0','repo':'CODEX','authority':'operational_non_evidence','probes':r},sort_keys=True))
