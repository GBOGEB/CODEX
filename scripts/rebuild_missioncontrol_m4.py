"""Rebuild the additive CODE PURPLE G4P M4 review page from governed source.

This is an HTML projection, not a Mycelium controller/worker dispatch implementation.
Pass --check in CI to refuse drift between CSS/JS/data and the generated page.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'docs/missioncontrol_operations_atlas.html'
DATA = ROOT / 'docs/data/missioncontrol_m4_status.json'
JS = ROOT / 'scripts/missioncontrol_m4_review.js'
CSS = ROOT / 'scripts/missioncontrol_m4_review.css'
OUT = ROOT / 'docs/missioncontrol_operations_atlas_m4.html'
BASE_BLOB = '9b2a09eb7c4b4c718e9cd4924020121bc197f931'


def blob_sha(raw: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\x00' + raw).hexdigest()


def build():
    old = BASE.read_bytes()
    if blob_sha(old) != BASE_BLOB:
        raise ValueError('HOLD: V2 source HTML has advanced; reconcile before rendering M4')
    old = old.decode('utf-8')
    data = json.loads(DATA.read_text(encoding='utf-8'))
    assert data['schema'] == 'missioncontrol.g4p.status_overlay.m4.v1'
    assert len(data['pr_merges']) == 21 and len(data['issues']) == 6
    assert data['authority']['main_admission'] == 'HOLD'
    assert data['authority']['mutation_enabled'] is False
    assert data['authority']['authenticated_worker_dispatch'] is None
    assert data['coverage'][1]['covered'] - data['coverage'][0]['covered'] == -3
    assert data['coverage'][1]['eligible'] - data['coverage'][0]['eligible'] == -2
    raw = json.dumps(data, sort_keys=True, separators=(',', ':'), ensure_ascii=True)
    if '<' in raw: raise ValueError('HOLD: unsafe raw JSON embedding')
    css, js = CSS.read_text(encoding='utf-8'), JS.read_text(encoding='utf-8')
    if not js.endswith('\n') or 'window.MissionControlReview' not in js:
        raise ValueError('HOLD: missing annotation source')
    if old.count('</style>') != 1 or old.count('</body>') != 1:
        raise ValueError('HOLD: V2 source markers drift')
    html = old.replace('</style>', css + '\n</style>', 1)
    html = html.replace('</body>', '<script id="m4-source" type="application/json">' + raw + '</script>\n<script>\n' + js + '\n</script>\n</body>', 1)
    return html


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--check', action='store_true')
    group.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = build()
    if args.check:
        if OUT.read_text(encoding='utf-8') != result:
            raise SystemExit('HOLD: generated M4 HTML is stale')
    else:
        OUT.write_text(result, encoding='utf-8')
    print(json.dumps({'result': 'PASS', 'mode': 'CHECK' if args.check else 'WRITE',
                      'semantic_snapshot': '2026-10-17T19:31:00Z',
                      'html_sha256': hashlib.sha256(result.encode('utf-8')).hexdigest(),
                      'merge_admission': 'HOLD'}))

if __name__ == '__main__': main()
