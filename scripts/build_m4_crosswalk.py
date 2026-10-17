"""Project selected M4 status evidence into a readable Mermaid + SIPOC dependency crosswalk."""
from pathlib import Path
import json, re
ROOT=Path(__file__).resolve().parents[1]
D=json.loads((ROOT/'docs/data/missioncontrol_m4_status.json').read_text())
REPO_ID={'CODEX':'CODEX','ABACUS':'ABACUS','HUB':'HUB','QPS':'QPS','MATH':'MATH'}
lines=['flowchart LR','  %% CODE PURPLE G4P M4 source-bound status overlay; worker authority DENY.']
for name in REPO_ID:
    lines.append(f'  repo_{name}["{name} · repository owner"]')
for pr in D['pr_merges']:
    key=f'pr_{pr["repo"]}_{pr["number"]}'
    label=f'{pr["repo"]} #{pr["number"]} · {pr["summary"][:30]}'
    label=label.replace('"',"'")
    lines.append(f'  {key}["{label}"]')
for i in D['issues']:
    lines.append(f'  issue_{i["repo"]}_{i["number"]}{{"{i["repo"]} #{i["number"]} · OPEN"}}')
for key,title in [('scheduler','Read-only scheduler projection'),('gateway','CODEX Mycelium gateway'),('stage','Stage-only / proposal'),('owner','Owner-runner authorization'),('receipt','Run / job / attempt / SHA'),('admit','Admission HOLD'),('review','User review / local notes')]:
    lines.append(f'  {key}["{title}"]')
for pr in D['pr_merges']:
    lines.append(f'  repo_{pr["repo"]} -->|owns| pr_{pr["repo"]}_{pr["number"]}')
    lines.append(f'  pr_{pr["repo"]}_{pr["number"]} -.->|{pr["target_kind"]} merge, independent proof| review')
for i in D['issues']:
    lines.append(f'  repo_{i["repo"]} -->|unresolved| issue_{i["repo"]}_{i["number"]}')
lines += [
 '  repo_CODEX --> gateway', '  gateway -->|model only| scheduler',
 '  scheduler -->|proposal only| stage', '  stage -.->|no remote authority| owner',
 '  repo_ABACUS --> owner', '  owner -.->|requires owner lease| receipt',
 '  receipt -->|exact-head evidence only| admit',
 '  repo_HUB -->|source census / Top-21| review',
 '  admit -.->|HOLD independent governance & security| review',
 '  pr_ABACUS_2147 -->|merged to feature| pr_ABACUS_2133',
 '  pr_ABACUS_2155 -->|merged to feature| pr_ABACUS_2133',
 '  pr_CODEX_1068 -.->|review UI, not closure| issue_CODEX_1067',
 '  pr_HUB_669 -.->|QA follow-up| issue_HUB_638',
 '  pr_HUB_671 -.->|orchestration scope| issue_HUB_604',
 '  pr_ABACUS_2133 -.->|governance remains independent| issue_ABACUS_2087',
 '  classDef mergedMain fill:#123d34,stroke:#4cc9a4,color:#effffb',
 '  classDef mergedFeature fill:#1c2c4a,stroke:#769be6,color:#eff4ff',
 '  classDef pending fill:#473122,stroke:#e6b46e,color:#fff6e9',
 '  classDef barrier fill:#502830,stroke:#e18e9c,color:#fff3f5',
]
for p in D['pr_merges']:
    cl='mergedMain' if p['target_kind']=='main' else 'mergedFeature'
    lines.append(f'  class pr_{p["repo"]}_{p["number"]} {cl}')
for i in D['issues']:lines.append(f'  class issue_{i["repo"]}_{i["number"]} pending')
lines.append('  class admit,gateway barrier')
OUT=ROOT/'docs/missioncontrol_m4_owner_dependency.mmd'
OUT.write_text('\n'.join(lines)+'\n',encoding='utf-8')
assert OUT.read_text().count('-->')>0 and len(D['pr_merges'])==21

sipoc=r'''# Mission Control G4P M+4 — SIPOC, DAG and live/unverified boundary

**Source freeze:** 2026-10-17T19:31:00Z. The 21 PR samples are selected and exact-merge verified, not exhaustive of the 90-repository programme. **No remote worker dispatched.**

| Supplier | Input (authority) | Process / typed edge | Output / artifact | Consumer | Current gate |
|---|---|---|---|---|---|
| CODEX Mycelium | `execution_gateway_contract.yaml`, principal + source policy | Scheduler topological projection and staged permission checks | Nonmutating dispatch proposal | ABACUS owner | HOLD until authenticated local owner execution |
| ABACUS owner | Exact PR source head + source-owned tests | Native runner and first-red / branch arc evidence | Run/job/attempt + artifact with head SHA | Reviewers / MIP | Per-head CI and security distinct |
| Hub source census | 21-repo Top21 `FEDERATION_GRAPH_N11.json` | Normalize typed nodes, edges and file atoms | 716 nodes, 734 edges, 26,836 represented files (historical) | Mission Control review/UI | Source observation, not current dispatch |
| CODEX Atlas V2 | 4 frozen registry blobs / Mycelium controls | Source-owned 32-node, 43-edge projection | V2 HTML + Mermaid | M+4 review overlay | Existing source SHA pinned |
| G3A N13→N14 | Two changed Phase4 source SHAs | Branch-arc and eligible-denominator reconciliation | 220/562 → 217/560, ΔK=−3, ΔD=−2 | Scope owner | No like-for-like causal inference |
| HTML review users | Local annotations, comments, QA findings | Export notes JSON via `missioncontrol:annotation-saved` event | Browser-local notes, not GitHub comments | Owners after explicit import/review | No authority transfer |
| Independent reviewers | A10, security, policy, compatibility, exact-head CI | Non-compensating admission | HOLD or verified main merge SHA | Golden Thread consumers | HOLD |

## Source-bound lineage graph

- [Mermaid dependency graph](missioncontrol_m4_owner_dependency.mmd) — 21 merged PR nodes, six still-open issue nodes, repository owners, stage/worker/evidence gates.
- [Machine-readable status snapshot](data/missioncontrol_m4_status.json) — exact merge targets and source commitments.
- [Published candidate page](missioncontrol_operations_atlas_m4.html) — generated local review surface only until hosted/CI QA is independently verified.
- [Legacy V2 graph](missioncontrol_operations_atlas_v2.mmd) — 32/43 typed source model (not additive with Top21 716/734).

## Denominator change, not a quality claim

\[
K_{N13}=220,\quad D_{N13}=562,\quad K_{N14}=217,\quad D_{N14}=560.
\]

The display ratio difference is \(217/560 - 220/562 \approx -0.40\) percentage points, but Phase4 source and denominator changed. **It must not be ranked as like-for-like regression or improvement.** Four unchanged source files retain 175 branch arcs according to earlier certified review; the new M4 atlas does not independently recalculate all 181-file coverage.

## Worker dispatch: authority/observation separation

`repo -> source registry -> DAG -> scheduler projection -> STAGE_ONLY -> owner-local executor (not enabled via browser) -> exact-head native receipt -> security/review -> main admission`. All edges exposed by M4 are *navigational or proposed*, never executable. Feedback loops are next-pulse, not same-pulse scheduling cycles. M4 does not install, dispatch, rerun Actions, approve reviews or close issues.

## Open issue link policy

An accepted merged PR does not automatically satisfy the attached issue DoV. Keep CODEX #1067, CODEX #977, ABACUS #2136/#2087 and HUB #638/#604 **open** pending their explicit owner acceptance and fresh native/published QA. Annotation notes are non-authoritative until imported into an owner issue or PR and reviewed.
'''
(ROOT/'docs/missioncontrol_m4_SIPOC_AND_OWNER_CONTROL.md').write_text(sipoc,encoding='utf-8')
print({'mermaid_nodes':len(D['pr_merges'])+len(D['issues'])+len(REPO_ID)+7,'mermaid_lines':len(lines),'issue_nodes':len(D['issues'])})
