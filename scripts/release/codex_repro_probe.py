from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "release" / "CODEX_REPRO_RECEIPT.json"
OUT.parent.mkdir(exist_ok=True)
TARGETS = [
    ROOT / "VERSION.json",
    ROOT / "ssot" / "domain" / "repo" / "release.yaml",
    ROOT / "triage" / "requirements" / "GLOBAL_CREQ_REGISTRY.json",
]

def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

first = {str(p.relative_to(ROOT)): digest(p) for p in TARGETS}
second = {str(p.relative_to(ROOT)): digest(p) for p in TARGETS}
status = "PASS" if first == second else "FAIL"
payload = {"schema_version":"1.0","probe":"CODEX_REPRODUCIBILITY","status":status,"first":first,"second":second}
OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
print(json.dumps(payload, indent=2))
raise SystemExit(0 if status == "PASS" else 1)
