"""N8 add-on: source-owner-preserving native debugger evidence + MYCELIUM DAG.

Never equate runtime debugger proof with a joined LDAB causal root or a QPS
engineering decision. Never trust an artifact's own assertion of its source
identity when the GitHub native run identity disagrees. All operation is local.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from collections import Counter
from copy import deepcopy
from datetime import date
import hashlib, json, re, zipfile
from .graph import make_node, make_edge, project_metrics, sha256, require, full_sha
from .journal import seal, verify as verify_journal

SCHEMA='code-purple.mycelium.native-bridge.v1'
ALLOWED={'GBOGEB/cryoplant-project','GBOGEB/CODEX'}
N8=[('S-N8-NATIVE','S',[]),('I-N8-CUSTODY','I',['S-N8-NATIVE']),
    ('P-N8-QPS-LLDB','P',['I-N8-CUSTODY']),
    ('P-N8-CODEX-LLDB','P',['I-N8-CUSTODY']),
    ('P-N8-ABACUS-JOIN','P',['I-N8-CUSTODY']),
    ('P-N8-STATISTICS','P',['I-N8-CUSTODY']),
    ('O-N8-GRAPH','O',['P-N8-QPS-LLDB','P-N8-CODEX-LLDB','P-N8-ABACUS-JOIN','P-N8-STATISTICS']),
    ('C-N8-REENTRY','C',['O-N8-GRAPH'])]
SHA256_PATTERN=re.compile('[0-9a-f]{64}\\Z')


def sha_file(path:Path)->str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()


def _safe_zip(path:Path,expected:str)->dict:
    require(type(expected) is str and bool(SHA256_PATTERN.fullmatch(expected)), 'missing external native artifact SHA256')
    require(sha_file(path)==expected,'native ZIP differs from provider-published digest')
    with zipfile.ZipFile(path) as z:
        require(z.testzip() is None,'native ZIP CRC mismatch')
        names=z.namelist()
        require(len(names)==len(set(names)) and names,'duplicate/empty ZIP')
        for n in names:
            require(not n.startswith(('/', '\\')) and '\\' not in n and '..' not in Path(n).parts,'unsafe ZIP path')
            require(z.getinfo(n).file_size<4_000_000,'oversized evidence member')
        return {'paths':names,'bytes':path.stat().st_size,'sha256':expected}


def _json(z:zipfile.ZipFile,key:str)->dict:
    require(key in z.namelist(),'required native member missing: '+key)
    v=json.loads(z.read(key))
    require(type(v) is dict,'native evidence must be JSON object')
    return v


def qualify_native(archive:Path,obs:dict)->dict:
    """One run with pinned independent GitHub run/job/digest evidence."""
    require(type(obs) is dict and obs.get('repository') in ALLOWED,'unknown native evidence owner')
    require(full_sha(obs.get('source_sha')),'missing full GitHub run source SHA')
    require(type(obs.get('run_id')) is int and obs['run_id']>0,'run identity required')
    require(type(obs.get('attempt')) is int and obs['attempt']>0,'run attempt required')
    require(type(obs.get('job_id')) is int and obs['job_id']>0,'native job id required')
    require(obs.get('run_status')=='completed' and obs.get('run_conclusion')=='success','unqualified native run')
    require(obs.get('job_conclusion')=='success','skipped or failed native job')
    require(obs.get('artifact_id',0)>0 and type(obs.get('artifact_id')) is int,'artifact ID absent')
    external=_safe_zip(archive,obs.get('artifact_sha256'))
    with zipfile.ZipFile(archive) as z:
        if obs['repository']=='GBOGEB/cryoplant-project':
            s=_json(z,'debug_session.json'); t=_json(z,'debugger_telemetry.json'); r=_json(z,'qps_lldb_receipt.json')
            require(all(x.get('exact_head_sha')==obs['source_sha'] for x in [s,t,r]), 'QPS native source drift')
            require(s.get('session_id')==t.get('session_id')==r.get('session',{}).get('session_id'), 'debugger session join mismatch')
            require(r.get('telemetry',{}).get('session_id')==s.get('session_id'), 'embedded receipt session mismatch')
            require(s.get('repo')==t.get('repo')==r.get('repo')==obs['repository'],'native repo mismatch')
            require(s.get('qps_engineering_credit_delta')==0 and r.get('authority_guards',{}).get('qps_engineering_credit_delta')==0,'engineering credit forgery')
            require(t.get('compile_returncode')==t.get('debugger_returncode')==0,'debugger execution failed')
            steps=t.get('observed_steps')
            require(type(steps) is int and steps>0 and r.get('real_probe_steps')==steps, 'invalid native-step denominator')
            require(r.get('dov_status')=='PASS' and t.get('status')=='ACCEPT','debugger runtime receipt withheld')
            state='NATIVE_QPS_LLDB_RUNTIME_PROVEN'
            source_binding='EXACT_RUN_JOB_SESSION_MATCH'
            session_id=s['session_id']
            observed_steps=steps
            warnings=['RUNTIME_ONLY_NOT_ENGINEERING_COMPLIANCE','DOCKER_NODE_SKIPPED_NOT_SUCCESS','ABACUS_JOINED_ROOT_WITHHELD']
        else:
            dap=_json(z,'lldb_dap_live.json'); mcp=_json(z,'lldb_mcp_live.json')
            require(dap.get('status')=='ACCEPT' and dap.get('dov_status')=='PASS','CODEX LLDB-DAP status invalid')
            require(mcp.get('status')=='ACCEPT' and mcp.get('dov_status')=='PASS','CODEX LLDB-MCP status invalid')
            require(dap.get('authority_guards',{}).get('formal_engineering_credit_delta')==0,'CODEX engineering claim')
            embedded=dap.get('source_exact_sha')
            require(embedded is None or full_sha(embedded),'malformed internal CODEX source')
            source_binding='EXACT_RUN_MATCH' if embedded==obs['source_sha'] else 'INTERNAL_DAP_SOURCE_MISMATCH'
            state='NATIVE_CODEX_LLDB_ARTIFACT_VERIFIED' if source_binding=='EXACT_RUN_MATCH' else 'NATIVE_CODEX_LLDB_ARTIFACT_SOURCE_CONFLICT'
            session_id=None
            observed_steps=None
            warnings=['ABACUS_JOINED_ROOT_WITHHELD','QPS_REMOTE_ADMISSION_WITHHELD']
            if source_binding!='EXACT_RUN_MATCH':warnings.append('DO_NOT_CREDIT_DAP_AS_EXACT_RUN_SOURCE_PROOF')
    return {'schema':SCHEMA,'repository':obs['repository'],'source_sha':obs['source_sha'],
            'run_id':obs['run_id'],'attempt':obs['attempt'],'job_id':obs['job_id'],
            'artifact_id':obs['artifact_id'],'artifact_sha256':external['sha256'],
            'members_crc_verified':len(external['paths']),'evidence_class':'NATIVE_BYTE_VERIFIED',
            'native_runtime_state':state,'source_binding':source_binding,'session_id':session_id,
            'observed_steps':observed_steps,'warnings':warnings,'owner_root_closure':None,
            'join_to_abacus':None,'qps_engineering_credit_delta':0,'admission':'HOLD',
            'authority_transfer':False}


def extend(parent:dict, legacy:dict, source_evidence:list[dict],*,n7_digest:str)->tuple[dict,dict]:
    require(sha256(parent)==n7_digest,'N7 semantic parent changed')
    require(parent.get('schema')=='code-purple.mycelium.graph.v2','not canonical N7 projection')
    require({x['repository'] for x in source_evidence}==ALLOWED and len(source_evidence)==2, 'two genuine native owners required')
    prior=deepcopy(parent);nodes=prior['nodes'];edges=prior['edges'];ids={n['id'] for n in nodes}
    require('sipoc:N7:C-N7-HOLD' in ids,'missing N7 restart node')
    def n(k,title,kind,layer,owner,source,evidence='DECLARED',**extra):
        require(k not in ids,'duplicate atom/node');ids.add(k)
        nodes.append(make_node(k,title,kind,layer,owner=owner,source=source,evidence=evidence,**extra))
    def e(a,b,kind,layer,binding,source_ref,**more):
        require(a in ids and b in ids,'edge orphan')
        edges.append(make_edge(a,b,kind,layer,binding=binding,source_ref=source_ref,**more))
    for k,role,deps in N8:
        nid='sipoc:N8:'+k
        n(nid,k,'SIPOC_INSTANCE','SIPOC','GBOGEB/CODEX','CODE_PURPLE_N8_SIPOC_ADDENDUM',role=role,epoch='N8',mode='OBSERVE',state='READONLY_PROPOSAL')
        for dep in deps:e('sipoc:N8:'+dep,nid,'SIPOC_DEPENDENCY','SIPOC','DECLARED','N8_PULSE_DAG_v1')
    e('sipoc:N7:C-N7-HOLD','sipoc:N8:S-N8-NATIVE','TEMPORAL_SUCCESSOR','TEMPORAL','HISTORICAL','N7_SEALED_TO_N8')
    for ev in source_evidence:
        owner=ev['repository'];rid='native:'+str(ev['run_id']);artifact='artifact:'+str(ev['artifact_id'])
        require(ev['evidence_class']=='NATIVE_BYTE_VERIFIED' and ev['admission']=='HOLD','unbound native claim')
        n(rid,'Native workflow run '+str(ev['run_id']),'RUN','GOLDEN_THREAD',owner,
          'https://github.com/'+owner+'/actions/runs/'+str(ev['run_id']),evidence='RECEIPT_BOUND',source_sha=ev['source_sha'],conclusion='success',run_id=ev['run_id'],job_id=ev['job_id'])
        e(rid,'repo:'+owner,'OWNED_BY','FEDERATION','OBSERVED','GitHub/Actions native run')
        n(artifact,'GitHub artifact '+str(ev['artifact_id']),'NATIVE_ARTIFACT','GOLDEN_THREAD',owner,
          'GitHub Actions/artifacts/'+str(ev['artifact_id']),evidence='RECEIPT_BOUND',source_sha=ev['source_sha'],sha256=ev['artifact_sha256'])
        e(rid,artifact,'PROOF','GOLDEN_THREAD','RECEIPT_BOUND','Github artifact SHA-256 digest',proof_ref=ev['artifact_sha256'])
        anchor='sipoc:N8:P-N8-QPS-LLDB' if owner.endswith('cryoplant-project') else 'sipoc:N8:P-N8-CODEX-LLDB'
        e(artifact,anchor,'SUPPLIES','GOLDEN_THREAD','RECEIPT_BOUND','independently byte-verified ZIP',proof_ref=ev['artifact_sha256'])
        if ev['session_id']:
            sid='session:'+ev['session_id']
            n(sid,'QPS LLDB native session','DEBUG_SESSION','ATOMS',owner,'debug_session.json',evidence='RECEIPT_BOUND',
              source_sha=ev['source_sha'],observed_steps=ev['observed_steps'],state='NATIVE_RUNTIME_ONLY')
            e(artifact,sid,'PROOF','GOLDEN_THREAD','RECEIPT_BOUND','qps_lldb_receipt.json',proof_ref=ev['artifact_sha256'])
    # Cross owner references remain declared until ABACUS joined native root event observed.
    n('atom:N8:ABACUS-JOIN-WITHHELD','ABACUS joined BD-LDAB receipt absent', 'EVIDENCE_GAP','BD',
       'GBOGEB/ABACUS','https://github.com/GBOGEB/ABACUS/issues/1929',evidence='DECLARED',accepted_root_count=None)
    e('contract:ABACUS_BD_LDAB','atom:N8:ABACUS-JOIN-WITHHELD','REVERSE_PRESSURE','BD','DECLARED','ABACUS#1929')
    e('atom:N8:ABACUS-JOIN-WITHHELD','sipoc:N8:P-N8-ABACUS-JOIN','REFERENCE','BD','DECLARED','ABACUS#1929')
    s=project_metrics(prior,legacy)
    require(s['legacy_sipoc_retention']=={'numerator':8,'denominator':8},'N1 nodes pruned')
    require(s['legacy_edge_retention']=={'numerator':10,'denominator':10},'N1 edges pruned')
    require(s['legacy_pr_retention']=={'numerator':22,'denominator':22},'N1 PRs pruned')
    require(s['accepted_causal_root_closures'] is None,'root closure promoted')
    return prior,s


def audit_compare(evidence:list[dict])->dict:
    owners={e['repository'] for e in evidence}
    require(owners==ALLOWED,'missing native debugger owner')
    q=next(e for e in evidence if e['repository'].endswith('cryoplant-project'))
    c=next(e for e in evidence if e['repository'].endswith('CODEX'))
    return {'native_zip_evidence_owners':2,'qps_real_steps':q['observed_steps'],
            'qps_session_proven':q['session_id'] is not None,
            'codex_inner_source_matches_workflow':c['source_binding']=='EXACT_RUN_MATCH',
            'independent_paired_repeats':None,'matched_effect':None,
            'accepted_root_closures':None,'admission':'HOLD',
            'scope':'TWO_DIFFERENT_REPOS_AND_RUN_FAMILIES_NOT_COMPARABLE_COHORT'}