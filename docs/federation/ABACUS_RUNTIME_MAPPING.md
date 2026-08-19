# ABACUS Runtime Mapping

This document maps ABACUS work levels to review-first lifecycle contracts. It is documentation-only and does not implement runtime orchestration.

| Level | Purpose | Parent | Child | FF input | FB output | Closure rule |
| --- | --- | --- | --- | --- | --- | --- |
| PROGRAMME | Durable strategic container for a portfolio of governed work. | None | WAVE | Charter, constraints, risk posture, victory frame. | Programme report, accepted wave deltas, durable anchors. | Closes only when all child waves are closed or explicitly deferred with blockers. |
| WAVE | Major parallelizable delivery slice inside a programme or PR. | PROGRAMME | SUB-WAVE or PHASE | Intent, scope, boundary rule, dependency graph, victory criteria. | Universal Work Report, wave status, blocker/limitation separation. | Closes when victory criteria are met or boundary/blocker is reported. |
| SUB-WAVE | Optional subdivision for parallel tracks with a common wave goal. | WAVE | PHASE | Wave FF plus track ownership and reconciliation milestone. | Sub-wave report and reconciliation notes. | Closes when child phases reconcile without hidden conflicts. |
| PHASE | Ordered lifecycle stage such as FRAME, DEFINE, EXECUTE, VERIFY, REPORT, HOLD, or MERGE GATE. | WAVE or SUB-WAVE | SPRINT | Phase entry criteria and required evidence. | Phase evidence, state transitions, and unresolved gaps. | Closes only after required evidence is recorded or limitation is labeled. |
| SPRINT | Time-boxed or batch-sized execution package. | PHASE | TASK | Selected phase goals, scope limits, and test ledger expectations. | Sprint report, commits, tests, and feedback. | Closes when committed artifacts and report twin are updated. |
| TASK | Atomic deliverable with one owner and one outcome. | SPRINT | SUBTASK | Task contract, dependencies, files owned, victory target. | Task evidence, touched artifacts, blockers, and handoff target. | Closes when output is verified or blocked with follow-on feedback. |
| SUBTASK | Smallest executable unit, often a file or check. | TASK | None | Exact input, constraints, and expected result. | Result, evidence, and local limitation/blocker if any. | Closes when result is observed and reported upward. |

## FF / FB invariants

- A unit may not start without feedforward input from its parent or caller.
- A unit may not close without feedback output that can be rolled up.
- `SEQ` tracks serialize dependent work; `PAR` tracks may run independently but must reconcile at a milestone.
- Human-only merge gates remain outside agent closure authority.

## Review-first boundary

Runtime execution, API calls, CI enforcement, production automation, and merge actions are out-of-scope until a follow-on PR explicitly implements and approves them.
