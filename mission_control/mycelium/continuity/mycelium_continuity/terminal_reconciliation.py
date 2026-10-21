"""N10 terminal reconciliation of the N9 admission chronology.

Re-reads the exact N9 PR-head runs and appends a new observation; the N9
snapshot stays the immutable, hash-bound parent and is never rewritten. A run
that later turned terminal does not prove that a required status blocked the
merge, and a stable red/green outcome is not an independent admission review.
"""
from __future__ import annotations
from collections import Counter
from copy import deepcopy
from .admission_timeline import SCHEMA as PARENT_SCHEMA, validate as validate_parent, _utc, _posint, _ALLOWED_STATUSES, _ALLOWED_CONCLUSIONS
from .graph import make_node, make_edge, project_metrics, require, sha256, full_sha

SCHEMA = 'code-purple.mycelium.terminal-reconciliation.v1'
OUTPUT = 'code-purple.mycelium.terminal-reconciliation-projection.v1'
_N10 = [('S-N10-PARENT','S',()),('I-N10-READBACK','I',('S-N10-PARENT',)),
        ('P-N10-TERMINAL','P',('I-N10-READBACK',)),('P-N10-OWNERS','P',('I-N10-READBACK',)),
        ('O-N10-RECONCILE','O',('P-N10-TERMINAL','P-N10-OWNERS')),
        ('C-N10-HOLD','C',('O-N10-RECONCILE',))]
_PROTECTION_DETAIL={'FORBIDDEN','READABLE','UNAUTHENTICATED_PUBLIC_READBACK'}


def _gate(status:str, conclusion:str|None) -> str:
    if status!='completed': return 'HOLD_NONTERMINAL_EXACT_HEAD'
    if conclusion=='failure': return 'HOLD_FAILED_EXACT_HEAD'
    if conclusion=='success': return 'HOLD_UNVERIFIED_REQUIRED_STATUS'
    return 'HOLD_NON_GREEN_EXACT_HEAD'


def validate(data:dict, parent:dict) -> dict:
    validate_parent(parent)
    require(type(data) is dict and data.get('schema')==SCHEMA, 'reconciliation schema')
    require(data.get('observation_class')=='GITHUB_PUBLIC_REST_NON_ATOMIC_READBACK', 'readback evidence provenance')
    require(data.get('authority_transfer') is False and data.get('merge_authorized') is False and data.get('security_waiver') is False, 'unauthorized disposition')
    require(data.get('accepted_root_closures') is None, 'false root closure')
    link=data.get('parent')
    require(type(link) is dict and link.get('epoch')=='N9' and link.get('schema')==PARENT_SCHEMA, 'parent epoch binding')
    require(link.get('snapshot_sha256')==sha256(parent), 'N9 parent snapshot hash drift')
    observed=_utc(data.get('observed_at'))
    parent_owners={o['repository']:o for o in parent['owners']}
    owners=data.get('owners');cases=data.get('cases')
    require(type(owners) is list and type(cases) is list and cases, 'empty observation population')
    by_owner={}
    for owner in owners:
        require(type(owner) is dict and owner.get('repository') in parent_owners, 'foreign owner')
        repo=owner['repository']
        require(repo not in by_owner, 'duplicate repository owner')
        require(owner.get('branch')==parent_owners[repo]['branch'], 'default branch changed without disposition')
        require(full_sha(owner.get('sha')), 'owner source SHA')
        require(type(owner.get('protected')) is bool and type(owner.get('required_status_verified')) is bool, 'branch protection unobserved')
        require(type(owner.get('visible_ruleset_count')) is int and owner['visible_ruleset_count']>=0, 'invalid ruleset cardinality')
        require(owner.get('protection_detail') in _PROTECTION_DETAIL, 'protection detail provenance missing')
        by_owner[repo]=owner
    require(set(by_owner)==set(parent_owners), 'owner population drift')
    parent_cases={(c['repository'],c['pr'],c['run_id']):c for c in parent['cases']}
    seen=set()
    for case in cases:
        require(type(case) is dict, 'invalid case')
        _posint(case.get('pr'),'PR');_posint(case.get('run_id'),'run');_posint(case.get('run_attempt'),'run attempt')
        key=(case.get('repository'),case['pr'],case['run_id'])
        require(key in parent_cases, 'case absent from N9 parent')
        require(key not in seen, 'duplicated case')
        seen.add(key);p=parent_cases[key]
        require(case.get('head_sha')==p['head_sha'] and case.get('run_head_sha')==p['run_head_sha'], 'PR/run source drift from parent')
        require(case.get('event')=='pull_request', 'not PR head CI')
        status=case.get('run_status');conclusion=case.get('run_conclusion')
        require(status in _ALLOWED_STATUSES, 'invalid run status')
        require((status=='completed' and conclusion in _ALLOWED_CONCLUSIONS) or (status!='completed' and conclusion is None), 'false terminal status')
        require(case.get('run_created_at')==p['run_created_at'], 'run creation time rewritten')
        updated=_utc(case.get('run_updated_at'))
        require(updated>=_utc(p['run_updated_at']), 'run evidence time reversal')
        require(updated<=observed, 'run updated after observation')
        if p['run_status']=='completed' and (status,conclusion)!=(p['run_status'],p['run_conclusion']):
            # A terminal N9 outcome may only change through a recorded re-run.
            require(case['run_attempt']>1 and updated>_utc(p['run_updated_at']), 'terminal outcome rewritten without re-run')
    require(seen==set(parent_cases), 'N9 case dropped')
    require(observed>=max(_utc(c['run_updated_at']) for c in parent['cases']), 'observation predates parent')
    return {'sources':len(by_owner),'cases':len(cases)}


def project(data:dict, parent:dict) -> dict:
    validate(data,parent)
    parent_cases={(c['repository'],c['pr'],c['run_id']):c for c in parent['cases']}
    parent_owners={o['repository']:o for o in parent['owners']}
    owners={o['repository']:o for o in data['owners']}
    rows=[]
    for c in data['cases']:
        p=parent_cases[(c['repository'],c['pr'],c['run_id'])]
        merged=_utc(p['merged_at']);upd=_utc(c['run_updated_at'])
        status,conclusion=c['run_status'],c['run_conclusion']
        if p['run_status']!='completed':
            if status!='completed': transition='STILL_NONTERMINAL'
            elif conclusion=='failure': transition='NONTERMINAL_RESOLVED_FAILED'
            elif conclusion=='success': transition='NONTERMINAL_RESOLVED_SUCCESS'
            else: transition='NONTERMINAL_RESOLVED_OTHER'
        elif (status,conclusion)==(p['run_status'],p['run_conclusion']): transition='TERMINAL_STABLE'
        else: transition='TERMINAL_RERUN_CHANGED'
        timing='AFTER_MERGE' if upd>merged else 'NOT_AFTER_MERGE'
        rows.append({'repository':c['repository'],'pr':c['pr'],'url':f"https://github.com/{c['repository']}/pull/{c['pr']}",
                     'run_id':c['run_id'],'run_url':f"https://github.com/{c['repository']}/actions/runs/{c['run_id']}",
                     'head_sha':c['head_sha'],'merged_at':p['merged_at'],'run_attempt':c['run_attempt'],
                     'parent_status':p['run_status'],'parent_conclusion':p['run_conclusion'],
                     'run_status':status,'run_conclusion':conclusion,'run_last_update':c['run_updated_at'],
                     'transition':transition,'last_update_relative_to_merge':timing,'gate':_gate(status,conclusion),
                     'effective_required_status_proven':owners[c['repository']]['required_status_verified'],
                     'admission':'HOLD'})
    transitions=dict(Counter(r['transition'] for r in rows))
    resolved=sum(r['transition'].startswith('NONTERMINAL_RESOLVED') for r in rows)
    return {'schema':OUTPUT,
            'source':{'observation_class':data['observation_class'],'observed_at':data['observed_at'],
                      'snapshot_sha256':sha256(data),'parent_snapshot_sha256':data['parent']['snapshot_sha256'],'non_atomic':True},
            'metrics':{'cases':len(rows),'resolved_since_parent':resolved,
                       'still_nonterminal':transitions.get('STILL_NONTERMINAL',0),
                       'terminal_stable':transitions.get('TERMINAL_STABLE',0),
                       'terminal_rerun_changed':transitions.get('TERMINAL_RERUN_CHANGED',0),
                       'failed_now':sum(r['run_conclusion']=='failure' for r in rows),
                       'success_now':sum(r['run_conclusion']=='success' for r in rows),
                       'red_terminal_resolved_after_merge':sum(r['transition']=='NONTERMINAL_RESOLVED_FAILED' and r['last_update_relative_to_merge']=='AFTER_MERGE' for r in rows),
                       'owner_heads_moved':sum(owners[r]['sha']!=parent_owners[r]['sha'] for r in owners),
                       'effective_required_status_proven':sum(o['required_status_verified'] for o in owners.values()),
                       'accepted_root_closures':None,'eligible_statistical_trials':None,
                       'merged_with_pre_merge_terminal_success_proven':None},
            'transitions':transitions,'rows':rows,'owner_action':'VERIFY_EFFECTIVE_REQUIRED_CHECK_AND_RED_BLOCK_CANARY',
            'admission':'HOLD','authority_transfer':False,'dispatch_authorized':False,'root_closures':None}


def extend_graph(parent:dict, legacy:dict, projected:dict, *,parent_sha:str) -> tuple[dict,dict]:
    require(sha256(parent)==parent_sha, 'N9 parent semantic hash drift')
    require(parent.get('schema')=='code-purple.mycelium.graph.v2' and projected.get('schema')==OUTPUT, 'wrong graph input')
    require(projected['admission']=='HOLD' and projected['root_closures'] is None,'unqualified projection')
    g=deepcopy(parent);nodes=g['nodes'];edges=g['edges'];ids={x['id'] for x in nodes}
    require('sipoc:N9:C-N9-HOLD' in ids,'missing N9 lineage root')
    def node(id,title,kind,layer,owner,source,evidence='DECLARED',**kw):
        require(id not in ids,'duplicate promoted node');ids.add(id)
        nodes.append(make_node(id,title,kind,layer,owner=owner,source=source,evidence=evidence,**kw))
    def edge(a,b,kind,layer,binding,source_ref):
        require(a in ids and b in ids,'unresolved graph relationship')
        edges.append(make_edge(a,b,kind,layer,binding=binding,source_ref=source_ref))
    for k,role,deps in _N10:
        id='sipoc:N10:'+k
        node(id,k,'SIPOC_INSTANCE','SIPOC','GBOGEB/CODEX','CODE_PURPLE_N10_DAG',role=role,epoch='N10',mode='OBSERVE',state='READONLY_PROPOSAL')
        for parent_id in deps:edge('sipoc:N10:'+parent_id,id,'SIPOC_DEPENDENCY','SIPOC','DECLARED','N10_SIPOC_DAG')
    edge('sipoc:N9:C-N9-HOLD','sipoc:N10:S-N10-PARENT','TEMPORAL_SUCCESSOR','TEMPORAL','HISTORICAL','N9_HASH_BOUND_N10_NEXT')
    for row in projected['rows']:
        repo=row['repository'];prior=f"run-admission:{repo}:{row['run_id']}";rid=f"run-terminal:N10:{repo}:{row['run_id']}"
        require(prior in ids,'N10 case without N9 run lineage')
        node(rid,'Terminal re-readback '+str(row['run_id']),'RUN','CONTROL',repo,row['run_url'],evidence='OBSERVED',
             source_sha=row['head_sha'],status=row['run_status'],conclusion=row['run_conclusion'],transition=row['transition'])
        edge(prior,rid,'TEMPORAL_SUCCESSOR','TEMPORAL','OBSERVED',row['run_url'])
        edge(rid,'sipoc:N10:P-N10-TERMINAL','SUPPLIES','CONTROL','OBSERVED',row['run_url'])
        gate='gate-admission:'+repo
        require(gate in ids,'N10 owner without N9 gate lineage')
        if row['gate']!='HOLD_UNVERIFIED_REQUIRED_STATUS':
            edge(rid,'pr-admission:'+f"{repo}#{row['pr']}",'REVERSE_PRESSURE','CONTROL','OBSERVED','terminal exact-head CI is not green')
    for gate in sorted({'gate-admission:'+r['repository'] for r in projected['rows']}):
        edge(gate,'sipoc:N10:P-N10-OWNERS','REVERSE_PRESSURE','CONTROL','DECLARED','effective required status still unproven')
    require('atom:N9:CPQ-016' in ids,'missing CPQ-016 owner atom')
    edge('atom:N9:CPQ-016','sipoc:N10:C-N10-HOLD','REVERSE_PRESSURE','BD','DECLARED','CPQ-016 required-check canary still owner/admin')
    metrics=project_metrics(g,legacy)
    require(metrics['legacy_sipoc_retention']=={'numerator':8,'denominator':8},'N1 SIPOC branch omitted')
    require(metrics['legacy_edge_retention']=={'numerator':10,'denominator':10},'N1 SIPOC edges omitted')
    require(metrics['legacy_pr_retention']=={'numerator':22,'denominator':22},'N1 PRs omitted')
    require(metrics['accepted_causal_root_closures'] is None,'formal root closure unsupported')
    return g,metrics
