# CODEX BD Queue — Current

Status date: 2026-09-21  
Repository: `GBOGEB/CODEX`  
Queue baseline: `ab0508b05636c61a9ab8923f0b88df02e591bf17`

## Queue rule

Every open issue must be in exactly one state:

- `FIX_PR`: repository change required; issue must link to an active or next repair PR.
- `PROVE`: code path exists; execute exact-head/default-branch proof and close on evidence.
- `EXTERNAL_GATE`: repository code is not the first red; retain only the exact owner/admin action and re-entry proof.
- `PARENT_CONTROL`: umbrella/control issue; no duplicate implementation PR unless a new concrete defect is found.

Closed/superseded defects are removed from this active queue rather than retained as historical pressure.

## Active BD queue

| Rank | Issue | State | Current binding | Burn-down predicate |
|---:|---|---|---|---|
| 1 | #797 KEB child-disposition return + metrics | FIX_PR | PR #798 | exact-head CI green -> merge -> close child issue |
| 2 | #500 TRIAGE conversion gate | EXTERNAL_GATE | real builder/evidence execution is local Windows/OneDrive under ABACUS #635 | run real local evidence verification + approved builder A/B through `Invoke-QpsControlledRoundtrip.ps1`; re-enter CODEX only with retained production receipts |
| 3 | #753 QPS v6 publication lane | EXTERNAL_GATE | single-writer code proof passed; Pages source mode previously observed legacy | owner sets Pages source to GitHub Actions, rerun unchanged proof, then bind release/deployment receipt |
| 4 | #255 typed KEB maturation | PARENT_CONTROL | #795/#796 burned; #797/#798 is current bounded child | complete return/disposition + metric child, then reassess parent closure against the eight original maturation atoms |
| 5 | #324 QPS program-focus KEB coverage | PARENT_CONTROL | cross-domain semantic/evidence umbrella | consume child authority/evidence and issue bounded child defects only |
| 6 | #319 DMAIC wave control | PARENT_CONTROL | live capacity/governance process-control umbrella | update measured wave checkpoints; do not turn metrics into duplicate code debt |

## Burned in this pass

- #254 CLOSED — current-source full KEB Wave-02 re-proof run `35582858595` SUCCESS; zero findings; QPS TODO-002 already DONE and dispositioned.
- #675 CLOSED — Historian debugger/MCP census closed by merged PR #794 at `ab0508b0...`; `NO_ACTIVE_DEBUGGER_DEBT`.
- #795 CLOSED — typed KEB candidate finding taxonomy + semantic dedup merged in PR #796.
- #741 CLOSED — dashboard incident cleared by six consecutive clean scheduled runs.
- #237 CLOSED — reusable package pattern/index helper merged in PR #790.
- #343 CLOSED — typed KEB child artifact lineage merged in PR #789.
- #256/#257/#258/#261 CLOSED — executable KEB warm-up and runtime-truth chain completed.
- #492 CLOSED — workflow visibility blocker superseded by #494/#499; production execution belongs to #500.
- #780 CLOSED — HIST-BD-022 authority repair chain completed.

## Execution order

`#797 -> PR #798` is the only active repository-local implementation repair.

`#500` and `#753` are explicit external gates. Do not substitute hosted synthetic proof for #500 and do not weaken the Pages source-mode validator for #753.

Parent `#255` has one current bounded child (#797/#798). Parent controls `#324/#319` remain non-coding surfaces until a concrete current defect is split out.

## Stop condition

The queue is considered burned down when every remaining open item is either:
1. linked to an active bounded repair PR,
2. waiting on a named external action with an unchanged re-entry proof, or
3. explicitly retained as a parent/control issue with no unbound concrete defect.
