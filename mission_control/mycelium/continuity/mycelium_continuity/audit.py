"""Owner-preserving original-intent audit. Scores are proposed planning hypotheses."""
from __future__ import annotations
from collections import Counter

# Sourced expectations from N1 glossary/next pulse and the CODEX canonical README.
# This is a review/decision register: not source-owner acceptance or a root ledger.
FEATURES = [
 {"id":"INT-01","feature":"Preserve all N1 instance/PR history without rewriting it","status":"IMPLEMENTED_LOCAL_N7","decision":"PRESERVE","value":5,"effort":1,"owner":"MYCELIUM_ADAPTER","acceptance":"Exact 8 nodes, 10 edges, 22 PRs and original ZIP bytes verified"},
 {"id":"INT-02","feature":"Live five-repository heads and source/PR exact identity","status":"SOURCE_BOUND_SNAPSHOT_NOT_LIVE_POLL","decision":"GROW","value":5,"effort":2,"owner":"CODEX_FEDERATION_READONLY","acceptance":"Refresh an external connector receipt; stale snapshots do not auto-retain green"},
 {"id":"INT-03","feature":"Canonical ABACUS BD/LDAB root join","status":"PENDING_NATIVE_JOINED_RECEIPT","decision":"HOLD_OWNER","value":5,"effort":4,"owner":"ABACUS_1929","acceptance":"ABACUS native joined root receipt with source/scan/job/attempt/artifact hashes"},
 {"id":"INT-04","feature":"Native LLDB debugger sessions linked to LDAB causal hypotheses","status":"UNJOINED_DEBUG_EVIDENCE","decision":"GROW","value":4,"effort":4,"owner":"ABACUS_QPS_DEBUG_OWNER","acceptance":"Exact session/command/job/source artifact + debugger hypothesis classification"},
 {"id":"INT-05","feature":"Bounded authenticated executor / owner leases","status":"CODEX_STAGE_ONLY_MUTATION_DISABLED","decision":"HOLD_OWNER","value":5,"effort":5,"owner":"CODEX_977","acceptance":"Owner-approved scoped transport, replay/idempotency/lease, signed external return"},
 {"id":"INT-06","feature":"Six canonical CODEX MYCELIUM 2x3 views","status":"CANONICAL_CODEX_DESIGN_N1_SINGLE_VIEW","decision":"GROW","value":5,"effort":3,"owner":"CODEX_UI_GOVERNANCE","acceptance":"Six standalone interoperable review panels, responsive and functional"},
 {"id":"INT-07","feature":"Typed full federation/reference graph separate from executable DAG","status":"IMPLEMENTED_LOCAL_N7","decision":"PRESERVE","value":5,"effort":2,"owner":"MYCELIUM_ADAPTER","acceptance":"Full graph may cycle; SIPOC graph rejects cycle and orphan"},
 {"id":"INT-08","feature":"Atom identity, typed node/edge and visible in/out evidence level","status":"IMPLEMENTED_LOCAL_N7","decision":"GROW","value":4,"effort":2,"owner":"MYCELIUM_ADAPTER","acceptance":"Atomic sources, provenance, typed arrows, line weight and inspection in GUI"},
 {"id":"INT-09","feature":"Standalone MYCELIUM as discrete method without duplicating SSOT","status":"IMPLEMENTED_LOCAL_N7","decision":"PRESERVE","value":5,"effort":2,"owner":"CODEX_UI_GOVERNANCE","acceptance":"Pure Python CLI + offline GUI + explicit authority bridges"},
 {"id":"INT-10","feature":"Golden Thread append-only replay and knowledge-time selection","status":"NATIVE_MC_EXISTS_ADAPTER_PARTIAL","decision":"GROW","value":5,"effort":3,"owner":"MISSIONCONTROL_GOLDEN_THREAD","acceptance":"Hash event chain and known-at selection without replacing parent ledger"},
 {"id":"INT-11","feature":"SIPOC scheduler and bounded concurrency / path lease","status":"NATIVE_SIPOC_PLANNER_EXISTS_READONLY","decision":"PRESERVE","value":4,"effort":2,"owner":"MISSIONCONTROL_SIPOC","acceptance":"Use canonical process stage adapter; no second mutation dispatcher"},
 {"id":"INT-12","feature":"Evidence and breadth/coverage/penetration/reach metrics","status":"PARTIAL_SCOPED_COUNTS","decision":"GROW","value":5,"effort":3,"owner":"FEDERATION_STATISTICS","acceptance":"Explicit eligible denominators, proof class, comparable source scope; UNKNOWN allowed"},
 {"id":"INT-13","feature":"N-1 / N / N+1 matched causal and predictive statistics","status":"INFERENCE_WITHHELD","decision":"HOLD_EVIDENCE","value":5,"effort":4,"owner":"GG_MATH_METHOD","acceptance":"Independent matched trials, predeclared estimator and scored predictions"},
 {"id":"INT-14","feature":"Source control, A10, reviewer and security independent HOLD","status":"IMPLEMENTED_POLICY_NOT_ENFORCED_MAIN","decision":"HOLD_OWNER","value":5,"effort":3,"owner":"ABACUS_MC_ADMIN","acceptance":"Effective GitHub required status and red-block/green-admit canary"},
 {"id":"INT-15","feature":"Lossless restart at arbitrary later pulse","status":"LOCAL_ARCHIVES_AVAILABLE_NO_FULL_CHAT_EXPORT","decision":"GROW","value":5,"effort":2,"owner":"MYCELIUM_ADAPTER","acceptance":"Original archive byte-identical; append-only receipt; restart-pointer + provenance"},
 {"id":"INT-16","feature":"Responsive user navigator with graph zoom and lane filters","status":"N1_PARTIAL_N7_EXPANSION","decision":"GROW","value":4,"effort":2,"owner":"MYCELIUM_ADAPTER","acceptance":"3 viewports, node focus, layer filter, zoom, proof legend, no overflow"},
 {"id":"INT-17","feature":"Vendor tool examples (Kubernetes/TCP etc.) without measured feeder","status":"UNBOUND_INPUTS","decision":"DEFER_UNTIL_MEASURED","value":2,"effort":3,"owner":"RUNNER_TELEMETRY_PROVIDER","acceptance":"Named source and >=3 comparable measurements over >=2 missions"},
 {"id":"INT-18","feature":"Duplicate MYCELIUM dashboard or new independent BD ledger","status":"REDUNDANT_WITH_EXISTING_AUTHORITIES","decision":"PRUNE_CANDIDATE_ONLY","value":1,"effort":4,"owner":"CODEX_MC_SOURCE_OWNERS","acceptance":"Keep original bytes; deprecate duplicate rendering only after owner review"},
 {"id":"INT-19","feature":"Authoritative QPS child acceptance through federation","status":"EXTERNAL_OWNER_DEFER","decision":"HOLD_OWNER","value":5,"effort":5,"owner":"QPS_CHILD_ENGINEERING","acceptance":"Exact QPS child semantic owner receipt; no inheritance from hub green"},
 {"id":"INT-20","feature":"BD first-red, source lease and reverse-pressure fan-out","status":"NATIVE_MC_EXISTING_CONTRACTS_N7_GRAPH","decision":"GROW","value":5,"effort":3,"owner":"MC_BD_REX","acceptance":"First-red linked to canonical owner; no double credit; disjoint leases"}
]


def audit_summary() -> dict:
    items = []
    for f in FEATURES:
        row = dict(f)
        row['planning_value_per_effort'] = round(f['value']/f['effort'],3)
        row['score_evidence_class'] = 'POSTULATED_PLANNING_ONLY'
        row['source_basis'] = 'N1_SOURCE_OR_CODEX_MC_CONNECTOR_READBACK_AND_EXPLICIT_ANALYSIS'
        row['canonical_root_id'] = None
        items.append(row)
    return {'schema':'code-purple.mycelium.intent-audit.v2','authority_transfer':False,
            'root_closures':None,'scores_are_observed':False,
            'decision_counts':dict(Counter(i['decision'] for i in items)),
            'features':items,
            'prune_rule':'Never delete ancestor, evidence, alternative branch, negative outcome or owner authority; only review a redundant *presentation* after a documented owner disposition.',
            'staleness_rule':'Source head changes invalidate associated proof unless a source-nonimpact receipt explicitly proves reuse.',
            'evidence_limit':'N1 is a 6-entry local mesh projection, not a full conversation export; CODEX/MC sources observed by connector are not cloned inside this archive.'}


def markdown(audit: dict) -> str:
    header=['# Original-intent gap and branch-conservation audit','',
            'Origin: immutable N1 mesh and continuation-kit design. CODEX canonical six-view UI and gateway are remote source-owned. Scores below are **postulated planning estimates**, not experiment outcomes.','',
            '| ID | Envisioned capability | Evidence state | Decision | Value/Effort | Owner |',
            '|---|---|---|---|---|---|']
    body=[f"| {r['id']} | {r['feature']} | {r['status']} | {r['decision']} | {r['value']}/{r['effort']} | {r['owner']} |" for r in audit['features']]
    return '\n'.join(header+body+['','## Cull and prune policy','', audit['prune_rule'],'',
        'A `PRUNE_CANDIDATE_ONLY` is not a deletion. Unrealised methods remain discoverable with explicit holds and owner/source provenance.','',
        '## Evidence gaps','',audit['evidence_limit'],''])+'\n'