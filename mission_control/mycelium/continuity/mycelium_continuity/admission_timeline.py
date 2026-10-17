"""N9 admission chronology and MYCELIUM reverse-pressure projection.

Informational only; run.updated_at is NOT a certified terminal time. Neither a
merge nor a green later check proves that a required status blocked red heads.
The existing CODEX and Mission Control authority remains external.
"""
from __future__ import annotations
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
import html
import json
from pathlib import Path
import re
from .graph import make_node, make_edge, project_metrics, require, sha256, full_sha

SCHEMA = 'code-purple.mycelium.admission-observation.v1'
OUTPUT = 'code-purple.mycelium.admission-chronology.v1'
_N9 = [('S-N9-AUTHORITY','S',()),('I-N9-HEADS','I',('S-N9-AUTHORITY',)),
       ('P-N9-PR-CI','P',('I-N9-HEADS',)),('P-N9-GATES','P',('I-N9-HEADS',)),
       ('P-N9-ROOTS','P',('I-N9-HEADS',)),('P-N9-INFERENCE','P',('I-N9-HEADS',)),
       ('O-N9-VIEWS','O',('P-N9-PR-CI','P-N9-GATES','P-N9-ROOTS','P-N9-INFERENCE')),
       ('C-N9-HOLD','C',('O-N9-VIEWS',))]
_ALLOWED_STATUSES={'queued','in_progress','pending','waiting','completed'}
_ALLOWED_CONCLUSIONS={'success','failure','cancelled','timed_out','action_required','neutral','skipped','startup_failure'}
_HEAD_RE=re.compile(r'[0-9a-f]{40}\Z')


def _utc(value: str) -> datetime:
    require(type(value) is str and value.endswith('Z'), 'timestamp must be UTC Z')
    try:
        dt=datetime.fromisoformat(value[:-1] + '+00:00')
    except (ValueError,OverflowError) as e: raise ValueError('invalid source UTC timestamp') from e
    require(dt.tzinfo is not None, 'unbound timestamp')
    return dt


def _posint(value: object, label: str) -> None:
    require(type(value) is int and value>0, 'invalid '+label)


def validate(data:dict) -> dict:
    require(type(data) is dict and data.get('schema')==SCHEMA, 'admission readback schema')
    require(data.get('observation_class')=='GITHUB_CONNECTOR_NON_ATOMIC_READBACK', 'readback evidence provenance')
    require(data.get('authority_transfer') is False and data.get('merge_authorized') is False and data.get('security_waiver') is False, 'unauthorized disposition')
    require(data.get('accepted_root_closures') is None, 'false root closure')
    owners=data.get('owners')
    cases=data.get('cases')
    require(type(owners) is list and owners and type(cases) is list and cases, 'empty observation population')
    by_owner={}
    for owner in owners:
        require(type(owner) is dict and type(owner.get('repository')) is str and owner['repository'].startswith('GBOGEB/'), 'owner identity')
        repo=owner['repository']
        require(repo not in by_owner, 'duplicate repository owner')
        require(full_sha(owner.get('sha')), 'owner source SHA')
        require(owner.get('branch') in {'main','master'}, 'unknown default branch')
        require(type(owner.get('protected')) is bool, 'branch protection unobserved')
        require(type(owner.get('required_status_verified')) is bool, 'required status state unspecified')
        _posint(owner.get('visible_ruleset_count',-1)+1 if type(owner.get('visible_ruleset_count')) is int else -1,'ruleset cardinality')
        require(owner.get('protection_detail') in {'FORBIDDEN','NOT_RECHECKED_IN_N9','READABLE'}, 'protection detail provenance missing')
        by_owner[repo]=owner
    keys=set();runs=set()
    for case in cases:
        require(type(case) is dict and case.get('repository') in by_owner, 'foreign PR owner')
        repo=case['repository'];_posint(case.get('pr'), 'PR');_posint(case.get('run_id'),'run')
        require(full_sha(case.get('head_sha')) and full_sha(case.get('merge_sha')) and full_sha(case.get('run_head_sha')), 'PR/run full SHA missing')
        require(case['head_sha']==case['run_head_sha'], 'PR/run source mismatch')
        key=(repo,case['pr']);run=(repo,case['run_id'])
        require(key not in keys and run not in runs, 'duplicated PR or run')
        keys.add(key);runs.add(run)
        require(case.get('run_status') in _ALLOWED_STATUSES, 'invalid run status')
        conclusion=case.get('run_conclusion')
        require((case['run_status']=='completed' and conclusion in _ALLOWED_CONCLUSIONS) or (case['run_status']!='completed' and conclusion is None), 'false terminal status')
        require(case.get('event')=='pull_request', 'not PR head CI')
        merged=_utc(case.get('merged_at'));created=_utc(case.get('run_created_at'));updated=_utc(case.get('run_updated_at'))
        require(created<=updated, 'run evidence time reversal')
        require(merged>=created, 'merge predates observed PR-head run')
    return {'sources':len(by_owner),'cases':len(cases)}


def project(data:dict) -> dict:
    validate(data)
    by_owner={r['repository']:r for r in data['owners']}
    rows=[]
    for c in data['cases']:
        merged=_utc(c['merged_at']);upd=_utc(c['run_updated_at'])
        if c['run_status']!='completed':
            disposition='MERGED_WITH_NONTERMINAL_RUN_AT_READBACK'
            gate='HOLD_NONTERMINAL_EXACT_HEAD'
        elif c['run_conclusion']=='failure':
            disposition='MERGED_WITH_FAILED_RUN_LATER_UPDATED' if upd>merged else 'MERGED_WITH_FAILED_RUN_ALREADY_UPDATED'
            gate='HOLD_FAILED_EXACT_HEAD'
        elif c['run_conclusion']=='success':
            disposition='MERGED_WITH_SUCCESS_RUN_LATER_UPDATED' if upd>merged else 'MERGED_WITH_SUCCESS_RUN_ALREADY_UPDATED'
            gate='HOLD_UNVERIFIED_REQUIRED_STATUS'
        else:
            disposition='MERGED_WITH_OTHER_TERMINAL_DISPOSITION'
            gate='HOLD_NON_GREEN_EXACT_HEAD'
        owner=by_owner[c['repository']]
        # GitHub branch protected=false is observed; we do not infer a bypass action.
        qualified=owner['required_status_verified'] is True and c['run_status']=='completed' and c['run_conclusion']=='success' and upd<=merged
        # Even this does not qualify independent review/security; exact admission remains unknown.
        rows.append({'repository':c['repository'],'pr':c['pr'],'url':f"https://github.com/{c['repository']}/pull/{c['pr']}",
                     'head_sha':c['head_sha'],'merged_at':c['merged_at'],'merge_sha':c['merge_sha'],
                     'run_id':c['run_id'],'run_url':f"https://github.com/{c['repository']}/actions/runs/{c['run_id']}",
                     'run_status_at_readback':c['run_status'],'run_conclusion_at_readback':c['run_conclusion'],
                     'run_last_update':c['run_updated_at'],'disposition':disposition,'gate':gate,
                     'timing_only_required_status_candidate':qualified,
                     'owner_protected_readback':owner['protected'],
                     'effective_required_status_proven':owner['required_status_verified'],
                     'admission':'HOLD'})
    cats=dict(Counter(x['disposition'] for x in rows))
    return {'schema':OUTPUT,'source':{'observation_class':data['observation_class'],'snapshot_sha256':sha256(data),'non_atomic':True},
            'metrics':{'merges_sampled':len(rows),'nonterminal_at_readback':sum(r['run_status_at_readback']!='completed' for r in rows),
                       'observed_failed':sum(r['run_conclusion_at_readback']=='failure' for r in rows),
                       'observed_success':sum(r['run_conclusion_at_readback']=='success' for r in rows),
                       'effective_required_status_proven':sum(r['effective_required_status_proven'] for r in rows),
                       'accepted_root_closures':None,'eligible_statistical_trials':None,
                       'merged_with_pre_merge_terminal_success_proven':None},
            'dispositions':cats,'rows':rows,'owner_action':'VERIFY_EFFECTIVE_REQUIRED_CHECK_AND_RED_BLOCK_CANARY',
            'admission':'HOLD','authority_transfer':False,'dispatch_authorized':False,'root_closures':None}


def extend_graph(parent:dict, legacy:dict, projected:dict, *,parent_sha:str) -> tuple[dict,dict]:
    require(sha256(parent)==parent_sha, 'N8 parent semantic hash drift')
    require(parent.get('schema')=='code-purple.mycelium.graph.v2' and projected.get('schema')==OUTPUT, 'wrong graph input')
    require(projected['admission']=='HOLD' and projected['root_closures'] is None,'unqualified projection')
    g=deepcopy(parent);nodes=g['nodes'];edges=g['edges'];ids={x['id'] for x in nodes}
    require('sipoc:N8:C-N8-REENTRY' in ids,'missing N8 lineage root')
    def node(id,title,kind,layer,owner,source,evidence='DECLARED',**kw):
        require(id not in ids,'duplicate promoted node');ids.add(id)
        nodes.append(make_node(id,title,kind,layer,owner=owner,source=source,evidence=evidence,**kw))
    def edge(a,b,kind,layer,binding,source_ref):
        require(a in ids and b in ids,'unresolved graph relationship')
        edges.append(make_edge(a,b,kind,layer,binding=binding,source_ref=source_ref))
    for k,role,deps in _N9:
        id='sipoc:N9:'+k
        node(id,k,'SIPOC_INSTANCE','SIPOC','GBOGEB/CODEX','CODE_PURPLE_N9_DAG',role=role,epoch='N9',mode='OBSERVE',state='READONLY_PROPOSAL')
        for parent_id in deps:edge('sipoc:N9:'+parent_id,id,'SIPOC_DEPENDENCY','SIPOC','DECLARED','N9_SIPOC_DAG')
    edge('sipoc:N8:C-N8-REENTRY','sipoc:N9:S-N9-AUTHORITY','TEMPORAL_SUCCESSOR','TEMPORAL','HISTORICAL','N8_BYTE_SEALED_N9_NEXT')
    known_gates=set()
    for row in projected['rows']:
        repo=row['repository'];key=f"{repo}#{row['pr']}";pid='pr-admission:'+key;rid=f"run-admission:{repo}:{row['run_id']}"
        node(pid,key,'PR','CONTROL',repo,row['url'],evidence='OBSERVED',source_sha=row['head_sha'],review_scope='GOVERNANCE_CANDIDATE')
        node(rid,'Exact-head CI '+str(row['run_id']),'RUN','CONTROL',repo,row['run_url'],evidence='OBSERVED',source_sha=row['head_sha'],status=row['run_status_at_readback'])
        edge(rid,pid,'PROOF','CONTROL','OBSERVED',row['run_url'])
        edge(pid,'sipoc:N9:P-N9-PR-CI','SUPPLIES','CONTROL','OBSERVED',row['url'])
        gate='gate-admission:'+repo
        if gate not in known_gates:
            known_gates.add(gate)
            node(gate,'Unproven required-status '+repo,'GATE','CONTROL',repo,'GitHub branch/ruleset REST readback',evidence='OBSERVED',verified=False)
            edge(gate,'sipoc:N9:P-N9-GATES','REVERSE_PRESSURE','CONTROL','DECLARED','CPQ-016 owner/admin return')
        edge(gate,pid,'REVERSE_PRESSURE','CONTROL','DECLARED','effective required status absent or unverified')
    node('atom:N9:CPQ-016','CPQ-016 independent required-check canary','BD_ITEM','BD','GBOGEB/pipeline-automation-hub','https://github.com/GBOGEB/pipeline-automation-hub/issues/336',evidence='OBSERVED',owner_control='RETURN_OWNER')
    edge('atom:N9:CPQ-016','sipoc:N9:P-N9-GATES','REVERSE_PRESSURE','BD','DECLARED','CPQ-016 canonical owner')
    edge('atom:N8:ABACUS-JOIN-WITHHELD','sipoc:N9:P-N9-ROOTS','REVERSE_PRESSURE','BD','DECLARED','ABACUS #1929 still source owner')
    edge('sipoc:N9:P-N9-INFERENCE','sipoc:N9:C-N9-HOLD','REVERSE_PRESSURE','CONTROL','DECLARED','independent matched trials missing')
    metrics=project_metrics(g,legacy)
    require(metrics['legacy_sipoc_retention']=={'numerator':8,'denominator':8},'N1 SIPOC branch omitted')
    require(metrics['legacy_edge_retention']=={'numerator':10,'denominator':10},'N1 SIPOC edges omitted')
    require(metrics['legacy_pr_retention']=={'numerator':22,'denominator':22},'N1 PRs omitted')
    require(metrics['accepted_causal_root_closures'] is None,'formal root closure unsupported')
    return g,metrics


def render_html(projection:dict)->str:
    require(projection.get('schema')==OUTPUT and projection.get('admission')=='HOLD', 'unqualified review')
    raw=json.dumps(projection,sort_keys=True,separators=(',',':'),ensure_ascii=True).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
    return '''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>CODE PURPLE N9 | Admission Chronology</title><style>
:root{font-family:system-ui;color-scheme:dark;background:#0e1726;color:#edf2fa}*{box-sizing:border-box}body{margin:auto;max-width:1400px;padding:24px}h1{font-size:clamp(24px,4vw,40px)}.dim{color:#aab9d1}small{color:#aab9d1}a{color:#91dfff}input,select{background:#20314b;border:1px solid #5c789b;color:white;padding:10px;border-radius:7px}input{max-width:100%}.flex{display:flex;flex-wrap:wrap;gap:10px;margin:16px 0}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(155px,1fr));gap:12px}.tile{background:#1c2e47;border-radius:12px;padding:20px}.tile b{display:block;font-size:28px}main{overflow-x:auto}table{min-width:850px;width:100%;border-collapse:collapse}th,td{border-bottom:1px solid #344967;padding:12px;text-align:left;vertical-align:top}td{font-size:13px}.warn{color:#f3bb78}.small{font-size:12px;overflow-wrap:anywhere}@media(max-width:600px){body{padding:12px}.tile{padding:12px}table{min-width:0}thead{display:none}tbody,tr,td{display:block;width:100%}tr{margin:10px 0;padding:4px;border:1px solid #344967;border-radius:10px}td{border:0;padding:8px 10px;overflow-wrap:anywhere}td:nth-child(1){font-weight:600}td:nth-child(2){color:#9cdcee}}</style></head><body>
<p class="warn">READ-ONLY / SOURCE NON-ATOMIC / P0 HOLD</p><h1>CODE PURPLE — N9 Admission Chronology</h1>
<p class="dim">The fact that a PR merged is not an authenticated proof that security checks, independent review and effective status rules blocked red heads. Run updated_at is not the certified terminal timestamp.</p>
<div id="source" class="small"></div><section id="counts" class="grid"></section>
<div class="flex"><label for="search">Search <input id="search" type="search" placeholder="Repository, PR, run, disposition"></label><label for="filter">Outcome <select id="filter"><option value="ALL">All cases</option><option value="NONTERMINAL">Nonterminal</option><option value="FAILURE">Failed</option><option value="SUCCESS">Succeeded later/readback</option></select></label></div>
<main><table><thead><tr><th>PR / source</th><th>Native CI</th><th>Chronology</th><th>Gate</th></tr></thead><tbody id="cases"></tbody></table></main><p id="shown" class="dim"></p>
<p class="dim">CODEX MYCELIUM owns this projection only; CPQ-016's effective ruleset and canary are owner/admin responsibilities. ABACUS joined-root and QPS engineering acceptance remain independent.</p>
<script>const D=__PAYLOAD__;const E=v=>String(v??'UNKNOWN').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));document.getElementById('source').textContent='Source sha256: '+D.source.snapshot_sha256+' | Nonatomic: '+D.source.non_atomic;document.getElementById('counts').innerHTML=[['Sampled merges',D.metrics.merges_sampled],['CI nonterminal',D.metrics.nonterminal_at_readback],['Failed observed',D.metrics.observed_failed],['Success observed',D.metrics.observed_success],['Effective status proof',D.metrics.effective_required_status_proven]].map(x=>'<div class="tile">'+E(x[0])+'<b>'+E(x[1])+'</b></div>').join('');function draw(){const s=document.getElementById('search').value.toLowerCase(),f=document.getElementById('filter').value;const a=D.rows.filter(x=>(f==='ALL'||(f==='NONTERMINAL'&&x.run_status_at_readback!=='completed')||(f==='FAILURE'&&x.run_conclusion_at_readback==='failure')||(f==='SUCCESS'&&x.run_conclusion_at_readback==='success'))&&[x.repository,x.pr,x.run_id,x.disposition,x.gate].join(' ').toLowerCase().includes(s));document.getElementById('cases').innerHTML=a.map(x=>'<tr><td><a href="'+E(x.url)+'" target="_blank" rel="noopener noreferrer">'+E(x.repository)+' #'+E(x.pr)+'</a><div class="small">'+E(x.head_sha)+'</div></td><td><a href="'+E(x.run_url)+'" target="_blank" rel="noopener noreferrer">'+E(x.run_id)+'</a> / '+E(x.run_status_at_readback)+' / '+E(x.run_conclusion_at_readback)+'</td><td>'+E(x.disposition)+'<div class="small">Merged: '+E(x.merged_at)+' | Last run update: '+E(x.run_last_update)+'</div></td><td class="warn">'+E(x.gate)+'</td></tr>').join('');document.getElementById('shown').textContent=a.length+' of '+D.rows.length+' source cases';}document.getElementById('search').addEventListener('input',draw);document.getElementById('filter').addEventListener('change',draw);draw();</script></body></html>'''.replace('__PAYLOAD__',raw)