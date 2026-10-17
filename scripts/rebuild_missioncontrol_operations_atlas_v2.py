"""Regenerate pinned Operations Atlas v2 HTML/Mermaid from source JSON.

No network, no dispatch, no source admission promotion. --check is non-mutating.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'docs/data/missioncontrol_operations_atlas_v2.json'
PAGE=ROOT/'docs/missioncontrol_operations_atlas.html'
MERMAID=ROOT/'docs/missioncontrol_operations_atlas_v2.mmd'


def semantic_digest(obj):
    payload=json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=True)
    return hashlib.sha256(payload.encode('utf-8')).hexdigest()


def guard(obj):
    assert obj['schema']=='missioncontrol.federated.operations_atlas.v2'
    status=obj['snapshot']
    assert status['merge_admission']=='HOLD' and status['mutation_enabled'] is False
    assert status['authority_transfer'] is False and status['security_waiver'] is False
    assert status['authenticated_worker_launches'] is None
    assert status['canonical_master_dags_path'] is None
    nodes={n['id'] for n in obj['nodes']}
    assert len(nodes)==len(obj['nodes'])
    graph={n:[] for n in nodes}
    for e in obj['edges']:
        assert e['source'] in nodes and e['target'] in nodes
        if e['kind']=='dependency':graph[e['source']].append(e['target'])
        if e['kind']=='federation':
            assert e['executable'] is False and e['binding']=='DECLARED_EDGE_NO_RECEIPT'
    seen=set();stack=set()
    def walk(key):
        if key in stack:raise ValueError('same-pulse dependency cycle')
        if key in seen:return
        stack.add(key)
        for next_ in graph[key]:walk(next_)
        stack.remove(key);seen.add(key)
    for key in graph:walk(key)


def mermaid(obj):
    lines=['flowchart LR','%% Read-only. Source registries and federation candidates are not worker receipts.']
    for n in obj['nodes']:
        lines.append('  '+n['id']+'["'+n['label'].replace('"',"'")+'"]')
    for e in obj['edges']:
        arrow='-.->' if e['kind'] in ('federation','feedback_next_pulse','reference','candidate') else '-->'
        lines.append(f"  {e['source']} {arrow}|{e['kind']}| {e['target']}")
    lines.extend(['  classDef owner fill:#0d3552,stroke:#45ccbd,color:#e8f6ff',
        '  classDef withheld fill:#502b35,stroke:#f2bd70,color:#fff',
        '  class admission,owner_worker withheld',
        '  class repo_ABACUS,repo_CODEX,repo_HUB,repo_QPS,repo_MATH owner'])
    return '\n'.join(lines)+'\n'


def outputs():
    obj=json.loads(DATA.read_text(encoding='utf-8'))
    guard(obj)
    original=PAGE.read_text(encoding='utf-8')
    source=re.search(r'(<script id="atlas-data" type="application/json">)([\s\S]*?)(</script>)',original)
    digest_tag=re.search(r'(<code class="code" id="sourceDigest">)([0-9a-f]{64})(</code>)',original)
    if source is None or digest_tag is None:raise ValueError('missing HTML projection markers')
    compact=json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=True).replace('</','<\\/')
    result=original[:source.start(2)]+compact+original[source.end(2):]
    # Replace the current digest, not the old absolute offsets.
    result=re.sub(r'(<code class="code" id="sourceDigest">)[0-9a-f]{64}(</code>)',
                  lambda m:m.group(1)+semantic_digest(obj)+m.group(2),result,count=1)
    expected={DATA:json.dumps(obj,indent=2,sort_keys=True,ensure_ascii=True)+'\n',
              PAGE:result,MERMAID:mermaid(obj)}
    return expected


def main():
    ap=argparse.ArgumentParser()
    mode=ap.add_mutually_exclusive_group(required=True)
    mode.add_argument('--check',action='store_true')
    mode.add_argument('--write',action='store_true')
    args=ap.parse_args()
    expected=outputs()
    for path,content in expected.items():
        if args.check:
            if path.read_text(encoding='utf-8')!=content:
                raise SystemExit('HOLD: generated source drift at '+str(path))
        else:
            path.write_text(content,encoding='utf-8')
    print(json.dumps({'mode':'CHECK' if args.check else 'WRITE','files':len(expected),
                      'source':str(DATA),'result':'PASS','merge_admission':'HOLD'}))


if __name__=='__main__':main()
