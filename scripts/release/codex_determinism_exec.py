from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'release' / 'CODEX_DETERMINISM_RECEIPT.json'
OUT.parent.mkdir(exist_ok=True)
env = os.environ.copy()
env['PYTHONPATH'] = str(ROOT)

checks = [
    ('rc_preflight', [sys.executable, 'scripts/release/codex_rc_preflight.py'], ROOT / 'release' / 'CODEX_RC_PREFLIGHT.json'),
    ('repro_probe', [sys.executable, 'scripts/release/codex_repro_probe.py'], ROOT / 'release' / 'CODEX_REPRO_RECEIPT.json'),
]

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

results = {}
status = 'PASS'
for name, cmd, receipt in checks:
    hashes = []
    returncodes = []
    for _ in range(2):
        p = subprocess.run(cmd, cwd=ROOT, env=env, text=True, capture_output=True)
        returncodes.append(p.returncode)
        if p.returncode == 0 and receipt.exists():
            hashes.append(sha(receipt))
    same = len(hashes) == 2 and hashes[0] == hashes[1] and returncodes == [0, 0]
    results[name] = {'returncodes': returncodes, 'receipt_hashes': hashes, 'zero_delta': same}
    if not same:
        status = 'FAIL'

payload = {'schema_version':'1.0','gate':'CODEX_DETERMINISM_EXEC','status':status,'checks':results}
OUT.write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')
print(json.dumps(payload, indent=2))
raise SystemExit(0 if status == 'PASS' else 1)
