# CODE PURPLE — MIP Live-DAG convergence control (W1–W3)

## Project outcome

**One operational truth view, no fourth scheduler.** CODEX Mycelium owns typed orchestration projections; ABACUS DELTA_1 and source Actions own actual execution and telemetry; pipeline-automation-hub aggregates snapshots/visuals; QPS TRIAGE retains engineering child authority. Native GitHub Actions is the run/job/attempt authority. CODEX authenticated gateway remains STAGE_ONLY / mutation disabled. Nothing here authorizes merges.

## Existing assets to reuse

| Owner | Existing asset | Reuse |
|---|---|---|
| CODEX | `mission_control/mycelium/control_manifest.yaml` | typed edges, REX reverse pressure, independent engineering/control views |
| CODEX | `scripts/id_work_conserving_scheduler.py` | work-conserving priority, aging, checkpoints; projection not new scheduling authority |
| CODEX | `mission_control/mycelium/execution_gateway_contract.yaml` | fail-closed stage-only, exact head, idempotency, source owner |
| ABACUS | `runtime/execution/federated-execution-scheduler.yaml` | DELTA_1 coordination domains |
| ABACUS | `core/execution_backbone/backbone.py` | local bounded worker runtime; distinguish its queued vs executor-pending tasks |
| ABACUS | `tools/recovery/w32_runner_telemetry.py` | queue/execution p95, exact-head proof yield |
| ABACUS | `docs/ci/MCP_CAPACITY_EXPERIMENT.md` | authorized 2/4/8 pulse design with rollback |
| Hub | `mission-control/gogreen/mycelium_history/collect.py` | read-only native job history and source lineage |
| QPS | `triage/code_purple/dependency_spine/w30_offline_consumer.py` | bytes-verified but non-authoritative receiver, DEFER |

## MIP decision matrix

1. **Define:** native FAILURE ≠ downstream UPSTREAM_FAILED; waiting/owner DEFER ≠ occupied worker; queued GitHub job ≠ local executable ready task.
2. **Measure:** identity keys `(repo, workflow/run, attempt, job, head_sha)`; dependency task count and unique root-to-blocked reach; configured/verified pool slots, actual queue and service timestamps, verified artifact yield. Unknown input `null` never inferred as zero.
3. **Analyze:** duplicate run events, unbounded executor pending queue, path-lock collisions, backpressure, inherited failure amplification, stale exact-head, root recurrence and fixed/cohort denominator changes.
4. **Improve:** implement W1 operational task-state DAG and W2 monotonic native event reconciler. Integrate with existing scheduler by advisory task eligibility only; no second dispatcher.
5. **Control:** 27 named tests total across both W1/W2 test modules on four OS/Python cells; commit and exact-head native artifacts; no RED canary waiver. Formal goal requires authorized owner gates separately.

## Noncompensating KPI gates and baselines

| KPI | W1 fixture baseline (synthetic, NOT programme) | Measured N+1 acceptance |
|---|---|---|
| Primary vs blocked | 1 primary failure; 2 derived blocked descendants | zero conflation of native failure and derived upstream block in verified snapshot |
| Graph integrity | 7 tasks; 6 dependencies; DAG | 100% source-bound endpoints, no executable cycles |
| Identity/replay | 12 W2 replay/negative tests authored | 4/4 exact-head matrix terminal PASS and artifact presence |
| Pool occupancy | 1/1 Windows used; 0/0 owner pool is UNKNOWN utilization | zero unknown->zero substitution; actual pool capacity verified independently |
| Evidence proof | 0 verified native receipts in illustrative fixture | native task-based proof yield from real SHA/run/job/artifact identities |
| Native end-to-end | W1/W2 CI QUEUED at latest initial readback | 4/4 native matrix cells terminal with receipts; independent security |
| Governance | CODEX main `protected=false`; gateway mutations disabled | authorized reviewer, required contexts and blocked-RED negative canary; HOLD until then |

## Wave control / stop criterion

**W1 — STATIC/MEASURE**: publish read-only operational DAG observer. Exit after syntax/tests and 4 exact-head source-native jobs succeed.

**W2 — TEMPORAL/ANALYZE**: use event reconciliation to prohibit run/head drift, duplicate event credit, terminal overwrites, and older event reversion. Requires same four native jobs exercising **both** test modules.

**W3 — OBSERVATION/PROOF**: owner-authorized source snapshot adapter and native receipt validation; separately define `observed`, `derived`, `withheld` status classes. Compare N−1/N/N+1 on matched heads/scopes and run/attempt populations. Gate remains on HOLD unless independently qualified.

**W4 — POOL/CONTROL (future authorized lane)**: measure configured slots, actual free/occupied, pending executor backlog, queue p95, effective proof receipts/worker-hour; bounded ABACUS 2→4→8 experiment only if capacity authority and native measurement exist. No unbounded scaling. Stop increasing pool if throughput gain <10% or failures rise; revert on >30% productivity fall per existing experiment.

**Convergence:** require three comparable *native* repeated observation epochs with no unaccounted state regressions, complete proofs, and no outstanding P0 blockers. Synthetic fixture stability does **not** count. If any source root or gate remains blocked, switch to a disjoint admissible lane; do not loop reruns merely to manufacture progress.

## Operator readback

Latest code candidate is draft CODEX [PR #1116](https://github.com/GBOGEB/CODEX/pull/1116). Native run [39171683895](https://github.com/GBOGEB/CODEX/actions/runs/39171683895) was **queued** when inspected. Never assert its terminal result until fresh exact-head run/job/artifact readback. CODEX native transport remains STAGE_ONLY; QPS acceptance is separate.
