"""CLI build/verify of standalone read-only CODE PURPLE MYCELIUM continuity.

Examples:
  python -m mycelium_continuity.cli build --n1 INPUT.zip --readback pinned.json --out /tmp/n7
  python -m mycelium_continuity.cli verify --out /tmp/n7
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import sys
import zipfile
from pathlib import Path
from . import __version__
from .graph import project_metrics, sha256, validate_graph
from .ingest import build_graph
from .audit import audit_summary, markdown
from .journal import seal, verify as verify_journal, known_at
from .render import dashboard, mermaid_bd, mermaid_federation, mermaid_golden, mermaid_sipoc, static_svg

SCHEMA='code-purple.mycelium.release.v2'


def file_sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def safe_zip(path: Path) -> tuple[list[str], str]:
    with zipfile.ZipFile(path) as z:
        bad=z.testzip()
        if bad:raise ValueError('ZIP CRC failure: '+bad)
        names=z.namelist()
        for name in names:
            pp=Path(name)
            if pp.is_absolute() or '..' in pp.parts or '\\' in name: raise ValueError('unsafe ZIP member')
        return names,file_sha(path)


def write_json(p: Path, data: dict) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, sort_keys=True, indent=2, ensure_ascii=True)+'\n',encoding='utf-8')


def _journal_events(readback: dict, n1_digest: str, graph_digest: str, native_digest: str|None) -> list[dict]:
    day=readback['observed_on']
    common={'observed_on':day,'recorded_on':day,'admission':'HOLD','authoritative_mutation':False}
    records=[
       dict(id='N7-W1-SOURCE-FREEZE',type='SOURCE_FROZEN',evidence_class='HISTORICAL_INPUT',
            authority_domain='SOURCE_CUSTODY',subject='N1-original-zip',source_digest=n1_digest,
            **common),
       dict(id='N7-W1-GAP-AUDIT',type='INTENT_AUDITED',evidence_class='LOCAL_REPRODUCIBILITY',
            authority_domain='METHOD_AUDIT',subject='N1-20-feature-register',**common),
       dict(id='N7-W2-TOPOLOGY',type='TOPOLOGY_EXPANDED',evidence_class='LOCAL_REPRODUCIBILITY',
            authority_domain='CODEX_UI_GOVERNANCE',subject='N7-typed-mesh',source_digest=graph_digest,**common),
       dict(id='N7-W2-LEGACY-RETAINED',type='GATE_HELD',evidence_class='HISTORICAL_INPUT',
            authority_domain='MISSIONCONTROL_SIPOC',subject='8-10-22-preserved',**common)
    ]
    if native_digest:
        records.append(dict(id='N7-W3-NATIVE-596-ARTIFACT',type='NATIVE_METADATA_OBSERVED',
                            evidence_class='NATIVE_BYTE_VERIFIED',authority_domain='MISSIONCONTROL_CI',
                            subject='GitHub:12097153584',source_sha='a04a6dbc188811d56eaf19a0792685fc95bed745',
                            native_zip_sha256=native_digest,observed_on=day,recorded_on=day,
                            admission='HOLD',authoritative_mutation=False))
    records.append(dict(id='N7-W3-RECURSIVE-NEXT',type='NEXT_PULSE_PLANNED',
                        evidence_class='DECLARED_NEXT',authority_domain='CONTINUITY_ONLY',
                        subject='N8-native-federation-consumer',**common))
    return records


def render_docs(graph: dict,metrics: dict,audit: dict,readback: dict,orig: dict,n1_digest: str, native_digest: str | None = None) -> dict[str,str]:
    return {
     'DAG_SIPOC.mmd':mermaid_sipoc(graph),
     'DAG_FEDERATION.mmd':mermaid_federation(graph),
     'DAG_GOLDEN_THREAD.mmd':mermaid_golden(graph),
     'DAG_BD_REVERSE_PRESSURE.mmd':mermaid_bd(graph),
     'SIPOC.md':f'''# Recursive SIPOC federation (two preserved epochs)\n\n| Supplier | Input | Process | Output | Customer |\n|---|---|---|---|---|\n| User N1 original / earlier archives | byte-hashed historical mesh | Wave N7.1 SOURCE FREEZE + INTENT AUDIT | immutable N1 custody, gap register | CODEX Mycelium, owner\n| CODEX / Mission Control / ABACUS / QPS / gg_MATH | exact source heads and remote contracts | Wave N7.2 typed node/edge federation with separate dependency DAG | {metrics['nodes']} nodes / {metrics['edges']} edges, 5 planned SIPOC waves | Mission Control read-only GUI\n| Native MC workflow #39022625422 | byte-verified ZIP / run identity | Wave N7.3 golden-lineage overlay, local negative testflight | rendered HTML/SVG + QA manifest | user and canonical source owners\n| Independent security, owner and reviewer | approved native proof and effective main rules | explicit CONTROL decision, currently HOLD | owner disposition (no automatic promotion) | ABACUS/QPS release, future N8\n\n**Feedback:** re-read exact repo/PR heads, preserve all immutable inputs, compare knowledge-time vs event-time, append one observation, then recalculate the projection. Parallel process proposals are not authenticated agent launches.\n\nExecution topology: N1 8 original instances + N7 8 additional **declared** instances, five DAG waves. Original 10 N1 execution edges retained exactly. Universal graph cycles outside executable SIPOC DAG are permitted.\n''',
     'DEPENDENCIES.md':'''# Dependency and path-lease decisions\n\n- CODEX `mission_control/mycelium/control_manifest.yaml` is the canonical UI/intent surface; MYCELIUM continuity is an **adapter**, not a replacement.\n- Mission Control `mission-control/gogreen/sipoc_instances.py` is the canonical SIPOC scheduler. The embedded DAG is an offline projection.\n- Mission Control `mission-control/golden-thread/golden_thread.py` owns root/event replay. The N7 local hash journal proves custody only.\n- ABACUS issue #1929 remains the single BD-LDAB root register. N1 `root_id` strings are unverified historical candidates.\n- QPS owns child engineering acceptance. CODEX gateway remote mutation is denied by default.\n- CPQ-013 depends on CPQ-010 and sends reverse pressure to that owner, but no owner control handoff exists.\n- CPQ-016 requires a real owner-admin red-block/green-admit canary. The merged red #594 is not a waiver.\n- Prune decision `PRUNE_CANDIDATE_ONLY` applies to duplicate *projection/rendering*, never original evidence or source branches.\n''',
     'INTENT_AUDIT.md':markdown(audit),
     'STATUS.md':f'''# N7 measured scope and exact evidence\n\n| Dimension | Value | Class / restriction |\n|---|---:|---|\n| N1 SIPOC nodes preserved | {metrics['legacy_sipoc_retention']['numerator']}/8 | ORIGINAL_INPUT_SOURCE_MATCH |\n| N1 SIPOC edges preserved | {metrics['legacy_edge_retention']['numerator']}/10 | ORIGINAL_INPUT_SOURCE_MATCH |\n| N1 PR identities retained | {metrics['legacy_pr_retention']['numerator']}/22 | HISTORICAL_ONLY |\n| N7 typed graph nodes | {metrics['nodes']} | LOCAL_PROJECTION |\n| N7 typed graph edges | {metrics['edges']} | LOCAL_PROJECTION |\n| N7 source-labeled nodes | {metrics['scope_defined_node_provenance']['numerator']}/{metrics['scope_defined_node_provenance']['denominator']} | Source labels, not authenticated edge reach |\n| Current CPQ open | 9 of 18 | CONNECTOR_STATUS_READBACK_DAY_PRECISION |\n| Native run #39022625422 | SUCCESS | Exact PR head #596, separate artifacts |\n| Native ZIP SHA256 | {readback['pull_requests'][1]['native_artifact_sha256']} | {'DOWNLOAD_CRC_SHA256_VERIFIED' if native_digest else 'REMOTE_METADATA_ONLY_NOT_BYTE_REVERIFIED'} |\n| Native total fleet reach | UNKNOWN | Ineligible external denominator |\n| Root closure | UNKNOWN | Owner handoff not accepted |\n| Inferential statistical uplift | WITHHELD | Independent matched observations missing |\n\n**Important:** graph node growth vs the original 8-node SIPOC-only projection is a change in modeled ontology and scope, *not* 77 new executed functions. CODEX canonical six-panel UI exists in source, while this standalone is a review adapter. Historical source records do not become native CI admission through copying.\n''',
     'NEXT_PULSE.md':'''# N8 continuation / intervening DevOps recovery\n\n1. Verify ZIP/manifest and original N1/continuation archive SHA; load `RESTART_POINTER.json`.\n2. Refresh CODEX, ABACUS, Mission Control, QPS and gg_MATH default heads; record full SHA, observed-at, run/job/attempt and source blob hashes, never overwrite prior snapshots.\n3. Run `python -m mycelium_continuity.cli build --n1 ... --readback ... --out ...`; compare source-drift receipt and keep past green stale when any head changes.\n4. Load *canonical* CODEX Mycelium manifest; preserve six view identities and existing disabled gateway. Continue integrating only via read-only adapters.\n5. Bind a true native ABACUS joined `bd.ldab.joined.census.v1` artifact before labeling any root/LLDB session accepted. Distinguish debugger hypothesis vs native debugger execution.\n6. For CPQ-003/005, inspect actual native artifact screenshots/TTL and request owner DONE; for CPQ-010->013 require an ABACUS owner-controlled I2 handoff and source-matched recurrence. CPQ-016 needs owner/admin required-check canary.\n7. Re-run three-wave DMAIC/MIP pulse and native exact-SHA tests, then inspect independent A10/security/reviewer/required-status gates. Default HOLD.\n8. Preserve all previous ZIPs byte-exact. Append delta/lineage; never collapse original source branches into one dashboard without dispositions.\n\nDecision gates: code success != native fleet reach != QPS acceptance != formal root closure. No autonomous dispatch/merge/waiver.\n'''
    }


def build(n1zip: Path, readback: Path, out: Path, native: Path|None=None) -> dict:
    names,n1digest=safe_zip(n1zip)
    require=['mesh.json','GLOSSARY.md','NEXT_PULSE.md','QA_RECEIPT.json','index.html','screenshot_desktop.png']
    if any(n not in names for n in require):raise ValueError('missing N1 original member')
    with zipfile.ZipFile(n1zip) as z:
        original=json.loads(z.read('mesh.json'))
        try: legacy_qa=json.loads(z.read('QA_RECEIPT.json'))
        except Exception as e:raise ValueError('N1 QA missing') from e
    read=json.loads(readback.read_text(encoding='utf-8'))
    native_digest=None
    if native:
        _,native_digest=safe_zip(native)
        expected=read['pull_requests'][1]['native_artifact_sha256']
        if native_digest!=expected:raise ValueError('Native exact SHA ZIP digest mismatch')
    g=build_graph(original,read,verified_native_digest=native_digest)
    metrics=project_metrics(g,original)
    audit=audit_summary()
    out.mkdir(parents=True,exist_ok=True)
    for folder in ['data','diagrams','docs','proof','backing']:(out/folder).mkdir(exist_ok=True)
    write_json(out/'data/graph.json',g)
    write_json(out/'data/metrics.json',metrics)
    write_json(out/'data/intent_audit.json',audit)
    write_json(out/'data/source_readback.json',read)
    write_json(out/'data/n1_original_mesh.json',original)
    write_json(out/'data/n1_original_qa.json',legacy_qa)
    journal=seal(_journal_events(read,n1digest,sha256(g),native_digest))
    verify_journal(journal)
    write_json(out/'data/continuity_journal.json',journal)
    write_json(out/'data/knowledge_as_of_snapshot.json',known_at(journal,read['observed_on']))
    write_json(out/'data/graph_relationships.json',{'node_ids':[n['id'] for n in g['nodes']], 'edge_keys':[[e['from'],e['to'],e['kind'],e['binding']] for e in g['edges']]})
    write_json(out/'RESTART_POINTER.json',{
        'schema':'code-purple.mycelium.restart-pointer.v2',
        'current_pulse':'N7-W3-LOCAL_TESTFLIGHT',
        'previous_pulses':['N7-W1-INTENT_CUSTODY','N7-W2-TYPED_TOPOLOGY'],
        'primary_readback_on':read['observed_on'], 'original_n1_sha256':n1digest,
        'graph_sha256':sha256(g),'continuity_journal_head':journal['head_digest'],
        'canonical_merge_admission':'HOLD', 'root_closures':None,
        'next_action':'native CODEX review and ABACUS joined owner receipt',
        'no_background_execution':True})
    for name,body in render_docs(g,metrics,audit,read,original,n1digest,native_digest).items():
        sub='diagrams' if name.endswith('.mmd') else 'docs'
        (out/sub/name).write_text(body,encoding='utf-8')
    for layer in ('SIPOC','FEDERATION','BD','GOLDEN_THREAD'):
        (out/'diagrams'/f'{layer.lower()}.svg').write_text(static_svg(g,layer),encoding='utf-8')
    with (out/'data/nodes.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=['id','title','kind','layer','owner','evidence','source']);w.writeheader();w.writerows([{k:x.get(k) for k in w.fieldnames} for x in g['nodes']])
    with (out/'data/edges.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=['from','to','kind','layer','binding','source_ref']);w.writeheader();w.writerows([{k:x.get(k) for k in w.fieldnames} for x in g['edges']])
    cpq=sum(x['state'] in {'ACTIVE','TODO','UNKNOWN_NEEDS_READER'} for x in read['cpq_statuses'])
    payload={'release_id':'N7','graph':g,'metrics':metrics,'audit':audit,'live':read,
             'n1_sha256':n1digest,'graph_sha256':sha256(g),'cpq_open':cpq,
             'native_artifact_sha256':native_digest}
    (out/'index.html').write_text(dashboard(payload),encoding='utf-8')
    (out/'README.md').write_text('''# CODE PURPLE MYCELIUM N7 — standalone read-only continuity kit\n\nThis ZIP preserves N1 historical branches byte-for-byte and contains an additive CODEX-style six-panel review adapter. It is NOT a replacement for CODEX Mycelium governance, Mission Control Golden Thread or SIPOC, ABACUS BD-LDAB, or QPS semantic SSOT. It is not a complete ChatGPT conversation export.\n\nOpen `index.html` (offline); inspect `docs/INTENT_AUDIT.md`, `docs/STATUS.md`, `docs/SIPOC.md` and the four Mermaid/SVG diagrams; use `RESTART_POINTER.json` to continue. Verify `MANIFEST_SHA256.json` with `python -m mycelium_continuity.cli verify --out PATH`. Original N1 and preceding ZIPs are in `backing/` when packaged.\n\nFor a fresh source observation create a new file using exact connector identities; **do not overwrite** data/source_readback.json from this checkpoint. Regenerate with `python -m mycelium_continuity.cli build --n1 N1.zip --readback new.json --native exact_native.zip --out OUT`.\n\nTest: `python -m unittest discover -s tests -p 'test_*.py' -v` from the source root. Browser QA: `python qa/browser_qa.py --html RELEASE/index.html --out QA`. All code is Python stdlib except optional Playwright UI checks.\n\nAuthority: `P0_ADMISSION=HOLD`; `CODEX_DISPATCH=STAGED_NOT_LAUNCHED`; `ROOT_CLOSURES=UNKNOWN`; `QPS_CHILD=DEFER`. Neither graphs nor local tests are accepted root closures.\n''',encoding='utf-8')
    if n1zip.resolve()!= (out/'backing'/n1zip.name).resolve():
        (out/'backing'/n1zip.name).write_bytes(n1zip.read_bytes())
    if native:
        (out/'backing'/native.name).write_bytes(native.read_bytes())
    manifest={str(p.relative_to(out)):file_sha(p) for p in out.rglob('*') if p.is_file() and p.name!='MANIFEST_SHA256.json'}
    write_json(out/'MANIFEST_SHA256.json',{'schema':SCHEMA,'generator_version':__version__,
        'source_n1_sha256':n1digest,'source_readback_sha256':file_sha(readback),
        'manifest_file_count':len(manifest),'files_sha256':manifest,'evidence_level':'LOCAL_REPRODUCIBILITY',
        'root_credit':None,'native_historical_artifact_digest':native_digest,'admission':'HOLD'})
    return {'nodes':metrics['nodes'],'edges':metrics['edges'],'open':cpq,'files':len(manifest),
            'n1_sha256':n1digest,'graph_sha256':sha256(g),'journal_head':journal['head_digest']}


def verify(out: Path) -> dict:
    p=out/'MANIFEST_SHA256.json'
    info=json.loads(p.read_text(encoding='utf-8'))
    if info['schema']!=SCHEMA:raise ValueError('unexpected release schema')
    found={str(p.relative_to(out)):file_sha(p) for p in out.rglob('*') if p.is_file() and p.name!='MANIFEST_SHA256.json'}
    if found!=info['files_sha256']:raise ValueError('bundle members missing, added or altered')
    g=json.loads((out/'data/graph.json').read_text(encoding='utf-8'))
    original=json.loads((out/'data/n1_original_mesh.json').read_text(encoding='utf-8'))
    report=project_metrics(g,original)
    if report!=json.loads((out/'data/metrics.json').read_text(encoding='utf-8')):raise ValueError('metric parity invalid')
    verify_journal(json.loads((out/'data/continuity_journal.json').read_text(encoding='utf-8')))
    a=json.loads((out/'data/intent_audit.json').read_text(encoding='utf-8'))
    if len(a['features'])!=20:raise ValueError('missing intent/gap inventory')
    if sum(r['state'] in {'TODO','ACTIVE','UNKNOWN_NEEDS_READER'} for r in json.loads((out/'data/source_readback.json').read_text())['cpq_statuses'])!=9:raise ValueError('CPQ denominator drift')
    return {'files':len(found),'node_count':report['nodes'],'edge_count':report['edges'],
            'legacy_retention':True,'journal':True,'status':'PASS'}


def main(argv=None):
    a=argparse.ArgumentParser()
    sub=a.add_subparsers(dest='operation',required=True)
    b=sub.add_parser('build');b.add_argument('--n1',type=Path,required=True);b.add_argument('--readback',type=Path,required=True);b.add_argument('--out',type=Path,required=True);b.add_argument('--native',type=Path)
    v=sub.add_parser('verify');v.add_argument('--out',type=Path,required=True)
    args=a.parse_args(argv)
    if args.operation=='build':result=build(args.n1,args.readback,args.out,args.native)
    else:result=verify(args.out)
    print(json.dumps(result,sort_keys=True));return 0

if __name__=='__main__':sys.exit(main())