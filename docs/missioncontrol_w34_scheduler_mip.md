# CODE PURPLE W34 — dependency-ready and pool-aware scheduler MIP

**Owner:** CODEX / Mycelium. **Existing algorithm:** `scripts/id_work_conserving_scheduler.py` (aging/value density, setup affinity, deadline urgency). **New composition:** `scripts/id_scheduler_dependency_gate.py` checks source-bound READY dependency nodes, authenticated W33 receipt bytes, measured eligible pool availability, idempotency, and changed-path locks BEFORE selecting any non-executing proposal.

## D: Main defect/opportunity

The current work-conserving scheduler only knows QUEUED/RUNNING local microtasks. It cannot distinguish `UPSTREAM_FAILED_DERIVED` from native failure, cannot verify pool eligibility, and could propose work already blocked by an unmet owner/consumer edge. W33 CODEX operational DAG #1107 supplies native/derived states and five-axis provenance, but is a read-only projection rather than a dispatcher.

## M: independent denominators

- `stage_eligible/changed_path_disjoint/eligible_saturation` denominators are **synthetic-only** in W34 native tests unless a verified W33 source receipt and independently verified local pool inventory are supplied.
- Capacity unknown → DEFER_POOL_CAPACITY_UNKNOWN; full known pool → DEFER_POOL_FULL; unmet dependency → DEFER_DEPENDENCY; owner HOLD → DEFER_DEPENDENCY_OWNER_HOLD.
- Stale source head, replayed key, duplicate logical task, path collision, unsupported action and oversized proposal wave each preserve a separately typed first-red disposition.
- Real queue time P95, service P95, five-axis coverage, hit weights and worker cost stay UNKNOWN in the testfixture. Synthetic planning output is **not production throughput evidence**.

## I: bounded scaling and scheduling

Use the canonical `choose()` policy for value density/aging rather than inventing a new scheduler. Propose at most 4 actions per pulse, never more than verified free slots, never two proposals on intersecting paths in the same repository, and never stage a native or derived failure as ready. Cross-repo owner disjoint paths can be proposed concurrently, but every proposal remains `STAGED_NOT_DISPATCHED`.

## A: falsification

Native regression checks attack false source heads, forged proof manifest, missing/changed hash, unknown pool, overclaimed capacity, replay, duplicate task IDs, conflicting paths, budget >4, incorrect downstream state, owner hold and attempted remote mutations. No production pool capacity is invented. Four separate native OS/Python cells must return terminal results and SHA256-bounded **SIMULATED** receipts.

## C: stop/retrigger

Change-based re-entry: exact new source head, native run/attempt, changed proof artifact or independently verified pool availability. Never retry unchanged RED solely to re-run it. Scale from 1→2→4 *only* with verified pool inventory and measured marginal evidence yield; avoid repeated bad-value waves. After three matched epochs with bounded non-improving marginal value, park that lane with root/owner receipt, but preserve overall HOLD unless all independent targets and security/review gates are satisfied.

## SIPOC / dispatch boundary

CODEX Mycelium (supplier) → verified W33 task metrics and owner SHA (input) → validate readiness/pool/locks using existing work-conserving scheduler (process) → non-executing typed stage plan and hash receipt (output) → ABACUS owner, QPS owner and separate authenticated gateway (consumers).

**No actions triggered from the browser or W34 script.** CODEX #977 remains a necessary authenticated owner gateway and the current gateway contract has zero enabled mutation transports. Native green ≠ governance acceptance.
