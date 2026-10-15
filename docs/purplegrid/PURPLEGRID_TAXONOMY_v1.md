# PurpleGrid — CODE PURPLE umbrella vocabulary v1

Status: DRAFT PROPOSAL, non-executing. PurpleGrid is a user-facing umbrella for governed cross-repository observation, planning and evidence exchange. It is not a new authority, deployment, or command runtime.

## Preserve canonical identities
- CODE PURPLE: programme and governance invariants.
- QPS: GBOGEB/cryoplant-project, engineering source and final child acceptance.
- KEB: GBOGEB/CODEX, semantic contracts, vocabulary and routing.
- DOW: GBOGEB/ABACUS, independent verification and analysis.
- QPS TRIAGE: QPS + KEB + DOW, pre-existing cluster terminology.
- Mission Control: pre-existing orchestration and operator surfaces, not automatic cross-repo dispatch permission.
- BD/LDAB, CENSUS, MIP, DMAIC, EVERRED, REX: retain existing schemas and meanings.
- Char_BD / CBD!: proposed governed recovery campaign in ABACUS PR #2032, not an independent permission.

## Layers
| User name | Stable namespace | Purpose |
|---|---|---|
| CODE PURPLE | code_purple | Parent programme |
| PurpleGrid | purplegrid | Federation-wide operator vocabulary |
| Repository | repo | Independent source authority |
| Cluster | cluster | Declared federation cohort |
| Census | census | Scope enumeration and evidence gaps |
| Mission Control | mission_control | Governed execution planning |
| Bridge | bridge | Typed evidence exchange and receiver-bound returns |
| Char_BD | char_bd | Root-caused backlog recovery |

## Syntax and permission
Human-friendly proposed syntax: `GRID! <ACTION> scope=<repository|cluster|federation> target=<ID> mode=<read_only|dry_run|governed>`.

GRID! is a notation, NOT an installed CLI command. Default behavior for absent parameters is read-only/status; no implicit execution, deployment, synchronization or merge. Any mutating operation requires separately authorized principal, target, exact ref, path/action allowlist, idempotency, and independent controls.

## Small vocabulary
| Display | Semantic machine verb | Contract |
|---|---|---|
| STATUS | status | Report verified known state |
| START | init | Establish a missing non-destructive context |
| RESUME | resume | Continue from authenticated checkpoint |
| SEED | seed | Load explicitly declared initial reference inputs |
| FEED | ingest | Ingest authenticated native source evidence |
| REFRESH | refresh | Re-read authoritative upstream state |
| CENSUS | census | Enumerate a bounded population and missingness |
| ALIGN | reconcile | Identify conflicts and canonical owners; no implicit mutation |
| PLAN | plan | Compute eligibility-aware dependency DAG |
| RUN | execute | Execute only separately approved, bounded steps |
| CHECK | verify | Verify bytes, schema, native source and receipts |
| MEASURE | measure | Publish matched denominators and deltas |
| REPORT | publish_report | Publish suitable versioned evidence |
| CONTROL | control | Enforce existing controls, not rewrite them |

## Avoid semantic ambiguity
- UPDATE is forbidden as an operational verb: explicitly choose REFRESH (read), FEED (ingest), ALIGN (compare) or SYNC (authorized mutation).
- RESTART is forbidden without specifying RESUME, REINIT (context reconstruction), RERUN (new attempt), REPLAY (pinned inputs), or RESET (destructive, separately authorized).
- FULL means dependency-complete *planning*, followed by individually authorized eligible steps. Never treat FULL as blanket approval.
- A green Bridge CHECK does not prove authenticated transfer, REX acceptance, engineering acceptance, or formal credit.
- A passing test does not prove governed PR admission, accepted root closure or successful merge.
- UNKNOWN must remain null, never 0. Different coverage cohorts cannot establish numeric improvement.

## Suggested everyday phrases
`GRID! STATUS`: report only.
`GRID! REFRESH scope=federation`: re-read repository authorities.
`GRID! CENSUS scope=cluster target=qps_triage`: enumerate QPS/KEB/DOW with actual coverage and gaps.
`GRID! PLAN scope=federation`: compute DAG with HOLD conditions.
`GRID! BRIDGE CHECK target=qps_triage`: nonmutating native provenance verification.
`CBD! NEXT`: request next eligible governed root pulse, subject to independent authorization.

## Governance
authority_transfer=false; security_waiver=false; remote_mutation_enabled=false; auto_merge=false.
This proposal does not edit CODEX PIPELINE/GLOSSARY.yaml, existing tool interfaces, branch protections, transport policy or authorization. Any future parser/dispatcher is a separate governed implementation and must be tested with negative cases for stale SHAs, unauthorized principal, replay, route mismatch, absent approval and cross-repo authority transfer.
