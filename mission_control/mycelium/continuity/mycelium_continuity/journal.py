"""Local append-only continuity journal, NOT canonical Golden Thread event ledger.

It carries observations and testflight stages. Existing MC Golden Thread remains
sole owner of root/event replay semantics; this chain proves only local custody.
"""
from __future__ import annotations
from datetime import date, datetime
from copy import deepcopy
import hashlib
import json
from .graph import canonical_bytes, full_sha, require

SCHEMA='code-purple.mycelium.continuity-journal.v2'
EVENT_TYPES={'SOURCE_FROZEN','INTENT_AUDITED','TOPOLOGY_EXPANDED','TESTFLIGHT_EXECUTED','NATIVE_METADATA_OBSERVED','GATE_HELD','NEXT_PULSE_PLANNED','SOURCE_DRIFT_OBSERVED'}
CLASSES={'HISTORICAL_INPUT','CONNECTOR_METADATA','LOCAL_REPRODUCIBILITY','NATIVE_BYTE_VERIFIED','DECLARED_NEXT'}
GENESIS='0'*64


def _parse_date(day: str):
    require(type(day) is str and len(day)==10,'invalid day precision')
    try: return date.fromisoformat(day)
    except ValueError as ex: raise ValueError('invalid day value') from ex


def event_digest(e: dict) -> str:
    clean={k:v for k,v in e.items() if k!='digest'}
    return hashlib.sha256(canonical_bytes(clean)).hexdigest()


def seal(events: list[dict]) -> dict:
    require(type(events) is list, 'invalid journal sequence')
    prev=GENESIS
    clean=[]
    seen=set()
    for n,r in enumerate(events,start=1):
        r=deepcopy(r)
        require(r.get('id') and r['id'] not in seen,'duplicate/missing journal ID')
        seen.add(r['id'])
        require(r.get('type') in EVENT_TYPES,'unrecognized journal event type')
        require(r.get('evidence_class') in CLASSES,'unrecognized evidence class')
        _parse_date(r.get('recorded_on'))
        if r.get('observed_on') is not None:_parse_date(r['observed_on'])
        if r.get('source_sha') is not None:require(full_sha(r['source_sha']),'invalid event source SHA')
        require(r.get('authoritative_mutation') is False,'operational journal cannot mutate source authority')
        require(r.get('admission') == 'HOLD','journal cannot lift admission')
        if r['evidence_class'] == 'NATIVE_BYTE_VERIFIED':
            require(isinstance(r.get('native_zip_sha256'),str) and len(r['native_zip_sha256'])==64,'native artifact bytes unbound')
        r['seq']=n
        r['previous_digest']=prev
        r.pop('digest',None)
        r['digest']=event_digest(r)
        prev=r['digest']
        clean.append(r)
    return {'schema':SCHEMA,'events':clean,'head_digest':prev,'authority_transfer':False,
            'formal_credit_delta':0,'source_authority':'EXTERNAL_CANONICAL_GOLDEN_THREAD_NOT_THIS_JOURNAL'}


def verify(journal: dict) -> bool:
    require(journal.get('schema') == SCHEMA, 'incorrect continuity journal schema')
    require(journal.get('authority_transfer') is False and journal.get('formal_credit_delta') == 0,'journal unauthorized state')
    prev=GENESIS
    for n,e in enumerate(journal.get('events', []),1):
        require(e.get('seq')==n, 'journal sequence gap')
        require(e.get('previous_digest')==prev,'journal previous digest changed')
        require(e.get('digest')==event_digest(e),'journal content/digest changed')
        prev=e['digest']
    require(journal.get('head_digest')==prev,'journal final digest wrong')
    # Also re-run invariant validations, not just hash consistency.
    require(seal([{k:v for k,v in e.items() if k not in ('seq','previous_digest','digest')} for e in journal['events']])==journal,'invalid or replay-forged journal')
    return True


def known_at(journal: dict, recorded_by: str, observed_by: str|None=None) -> dict:
    verify(journal)
    know=_parse_date(recorded_by)
    occurred=_parse_date(observed_by) if observed_by else None
    selected=[]
    for e in journal['events']:
        if _parse_date(e['recorded_on'])>know: continue
        if occurred is not None and (e.get('observed_on') is None or _parse_date(e['observed_on'])>occurred): continue
        selected.append(e)
    return {'schema':'code-purple.mycelium.knowledge-selection.v2',
            'full_verified_parent_digest':journal['head_digest'],
            'recorded_by':recorded_by,'observed_by':observed_by,
            'selected_events':selected,'selection_is_chain_prefix':selected == journal['events'][:len(selected)],
            'root_closure_credit':None,'admission':'HOLD'}


def drift(before: dict, after: dict) -> dict:
    require(before.get('schema')==after.get('schema')=='code-purple.source-readback.v1','incompatible source snapshot')
    old={r['repo']:r for r in before['repositories']}
    new={r['repo']:r for r in after['repositories']}
    require(set(old)==set(new),'changed target repository population')
    changes=[{'repo':repo,'before':old[repo]['sha'],'after':new[repo]['sha'],'invalidates_cached_native_proof':True}
             for repo in sorted(old) if old[repo]['sha'] != new[repo]['sha']]
    return {'schema':'code-purple.mycelium.source-drift.v2','source_head_changes':changes,
            'changed_count':len(changes),'automatic_prior_green_reuse':False,
            'would_promote_to_admission':False}