# Mission Control G4P M+4 — SIPOC, DAG and live/unverified boundary

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
