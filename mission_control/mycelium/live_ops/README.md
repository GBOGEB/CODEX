# MIP W1 — Live Operational DAG / pools / first-red pressure

A **read-only** materialized projection inside CODEX Mycelium. Reuse DELTA_1 and CODEX work-conserving scheduler; this module cannot run jobs, trigger Actions, vote on reviews, modify owner state, or grant root/engineering/admission credit. The checked-in W1 fixture is illustrative and **not live GitHub telemetry**.

**DMAIC:** Define the visibility gap between a primary failing native task and blocked descendants. Measure exact task IDs and timestamps plus configured capacity; unknown remains null. Analyse blocked amplification and queue P95 independently from proof yield. Improve by classifying upstream failure and deferred owners without occupying a worker. Control through fail-closed tests and SHA-pinned native qualification; repeat against real owner-authorized snapshot data before making production optimization claims.

**SIPOC:** GitHub native jobs + source owners → exact SHA/job/run/attempt, dependencies and pool configurations → validate/deduplicate/order/propagate → machine-readable task states, queue runtime P95, blocked descendants and proof denominator → CODEX Mycelium/Mission Control reviewer. No source-of-truth authority transfer.

**N:** 7 synthetic contract task nodes, 6 dependency edges, one primary failure and two blocked descendants; distinct independent Windows branch continues. **N+1 target:** signed/bound native job snapshot, enqueue vs executor-admitted times, task attempt history and retry safety. This is not a measured fleet improvement until live events arrive.

**Boundaries:** A task's native status and its derived upstream block are separate fields. Quiescent approvals/deferred work use zero execution slots, and no worker action can change a repo. Never pool heterogeneous run populations or mark undeclared pool capacity as observed GitHub host capacity. A source-verified native receipt must bind native run/job/attempt and artifact digest upstream.
