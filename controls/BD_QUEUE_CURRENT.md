# CODEX BD Queue — Current

Status date: 2026-09-21  
Repository: `GBOGEB/CODEX`  
Queue baseline: `d0f4e83e66bedc512e077ac05ac2ba8f289a530f`

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
| 1 | #741 Dashboard health check | FIX_PR | run 34936796143 reported 2 broken internal links | reproduce current link check, repair only live broken links, rerun dashboard health, close |
| 2 | #500 TRIAGE conversion gate | PROVE | W69/zero-delta mechanics exist; #492 visibility blocker retired | obtain real production `ZERO_DELTA_RECEIPT: PASS` + cluster receipt; close only on proof |
| 3 | #254 full QPS KEB exchange | PROVE | warm-up depth complete; #256/#257/#258/#261 closed | run source-SHA-bound full exchange and return child disposition |
| 4 | #753 QPS v6 publication lane | EXTERNAL_GATE | single-writer code proof passed; Pages source mode previously observed legacy | owner sets Pages source to GitHub Actions, rerun unchanged proof, then bind release/deployment receipt |
| 5 | #675 Historian debugger/MCP CONTROL | PARENT_CONTROL | concrete HIST-BD-014 repaired by #676 | finish historical classification; create repair PR only for surviving current-code debt |
| 6 | #255 typed KEB maturation | PARENT_CONTROL | executable warm-up mechanics landed #259/#262 | retain as reusable maturation parent; spawn only bounded concrete gaps |
| 7 | #324 QPS program-focus KEB coverage | PARENT_CONTROL | cross-domain semantic/evidence umbrella | consume child authority/evidence and issue bounded child defects only |
| 8 | #319 DMAIC wave control | PARENT_CONTROL | capacity/governance process-control umbrella | update measured wave checkpoints; do not turn metrics into duplicate code debt |

## Burned in this pass

- #237 CLOSED — reusable package pattern/index helper merged in PR #790.
- #343 CLOSED — typed KEB child artifact SHA-256/authority/semantic-change lineage merged in PR #789.
- #256 CLOSED — executable KEB warm-up run completed.
- #257 CLOSED — warm-up acceptance checklist satisfied.
- #258 CLOSED — QPS-FED-W01 lane reached CHILD_DISPOSITIONED/CLOSED.
- #261 CLOSED — runtime-truth defects repaired by #262 and proven in default-branch execution.
- #492 CLOSED — workflow registration/visibility blocker superseded by #494/#499; remaining zero-delta proof is #500.
- #780 CLOSED — HIST-BD-022 candidate-only authority repair landed through #781/#785/#786.

## Execution order

`#741` is now the only unbound repository-local repair.

In parallel, `#500` and `#254` are proof lanes because their underlying mechanics already exist.

`#753` is held at the explicit owner/admin gate; do not weaken the validator.

Parent controls `#675/#255/#324/#319` do not consume coding capacity unless they expose a new concrete current-code defect.

## Stop condition

The queue is considered burned down when every remaining open item is either:
1. linked to an active bounded repair PR,
2. waiting on a named external action with an unchanged re-entry proof, or
3. explicitly retained as a parent/control issue with no unbound concrete defect.
