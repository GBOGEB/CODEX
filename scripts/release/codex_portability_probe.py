from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RELEASE_DIR = ROOT / "release"
RELEASE_DIR.mkdir(exist_ok=True)
RECEIPT = RELEASE_DIR / "CODEX_PORTABILITY_RECEIPT.json"

checks = [
    [sys.executable, "-c", "from codex.ssot_resolver import resolve_ssot; print('resolver import PASS')"],
    [sys.executable, "tools/validators/ssot_validator.py"],
    [sys.executable, "tools/validators/master_input_validator.py"],
]

env = os.environ.copy()
env["PYTHONPATH"] = str(ROOT)
results: list[dict[str, object]] = []
status = "PASS"

for cmd in checks:
    proc = subprocess.run(cmd, cwd=ROOT, env=env, text=True, capture_output=True)
    results.append({
        "command": cmd,
        "returncode": proc.returncode,
        "stdout_tail": proc.stdout[-2000:],
        "stderr_tail": proc.stderr[-2000:],
    })
    if proc.returncode != 0:
        status = "FAIL"

payload = {
    "schema_version": "1.0",
    "probe": "CODEX_PORTABILITY",
    "status": status,
    "repo_root": str(ROOT),
    "python": sys.version.split()[0],
    "checks": results,
}
RECEIPT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
print(json.dumps(payload, indent=2))
raise SystemExit(0 if status == "PASS" else 1)
