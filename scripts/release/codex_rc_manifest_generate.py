from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'release' / 'CODEX_2_0_RC_MANIFEST.json'
OUT.parent.mkdir(exist_ok=True)
TARGETS = [
    ROOT / 'VERSION.json',
    ROOT / 'ssot/domain/repo/release.yaml',
    ROOT / 'triage/requirements/GLOBAL_CREQ_REGISTRY.json',
    ROOT / 'ssot/registry/logical_id_registry.yaml',
]

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

source_sha = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
version = json.loads((ROOT / 'VERSION.json').read_text(encoding='utf-8'))['version']
manifest = {
    'schema_version': '1.0',
    'release_program': 'CODEX_2_0',
    'target_version': '2.0.0',
    'current_product_version': version,
    'source_commit_sha': source_sha,
    'state': 'RC_MANIFEST_CANDIDATE',
    'files': {str(p.relative_to(ROOT)): sha256(p) for p in TARGETS},
    'promotion_allowed': False,
    'promotion_requires': ['release_smoke_pass','zero_delta_pass','adversarial_qa_pass','protected_main','formal_release'],
}
OUT.write_text(json.dumps(manifest, indent=2, sort_keys=True) + '\n', encoding='utf-8')
print(OUT.read_text())
