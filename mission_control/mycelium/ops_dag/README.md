# CODE PURPLE W33 — operational Mycelium task-instance overlay

**Owner:** CODEX Mycelium; **upstream authority:** ABACUS scheduler/DOW and individual native GitHub Actions; **outward projection:** HTML and machine JSON. No new scheduler/worker/gateway. Adopts the useful Airflow-style difference between actual FAILED and *derived* UPSTREAM_FAILED while retaining root provenance and dependency pressure. The universal genealogy/reference graph may cycle; only \`REQUIRES_SUCCESS\` edges form the acyclic execution projection.

## SIPOC

| Supplier | Input | Process | Output | Consumer |
|---|---|---|---|---|
| ABACUS B0 | actual source/head, matched eligibility | source/source-branch matching | proof/unknown | owner reviewer |
| Negative-path owner | native fault-oracle identities | adversarial fault execution | detected fault numerator | MIP |
| CODEX, ABACUS, QPS owner | two-sided native receipts | source/hash reconciliation | bound handshake/DEFER | QPS |
| GitHub runners | run/job/attempt and time | queue, runtime, eligible pool observation | bounded capacity evidence | scheduler |
| BD/REX owner | first-red log | fingerprint + downstream block graph | root candidates, no formal closure | REX |

## Frozen W33 first observation

\`W33_SELECTED_OBSERVATIONS.json\`: **13 native job instances**, 7 derived task/gate nodes, 17 edges. Historical ABACUS W29 N: four \`ModuleNotFoundError: scripts\` failures (one identical native-log fingerprint but four failed manifestations), with three downstream candidate stages (not additional failures). ABACUS W29 N+1: one Windows successful native job and three Ubuntu jobs queued at observed readback; ABACUS W32 B0 canonical failure; CODEX W30 four native successful jobs. No QPS private job metadata copied; QPS is represented as CODEX \`owner_hold\` with link to QPS #1959.

Each native observation retains exact SHA, run/job/attempt and URL. Its SHA may be historical relative to repo main; \`is_current_owner_head=false\` is exposed. A current HEAD alone never upgrades a historical job's conclusion. Queue/capacity/duration absent in native tool readback remain NULL/UNKNOWN.

### Stop/re-trigger / DMAIC programme contract

1. **Define** the source-root/descendant/eligibility population and owner/governance boundary.
2. **Measure** each of five growth denominators separately; native results, deduplicated fingerprint candidates, downstream blocked manifestations, queue/runtime P95 with sample \`n\`, source freshness, and only observed pool slots.
3. **Analyze** source first-red vs upstream derived block. For each instance, detect shared root signature without guessing formal causal closure. Source SHA and logical task selection must match for comparable temporal deltas.
4. **Improve** in independent owner slices. Ready tasks are merely **READY_PROPOSED**; this projection never dispatches. The CODEX authenticated execution gateway remains \`STAGE_ONLY\`; ABACUS/QPS acceptance rules stand separately.
5. **Control** via exact-head native regression, negative forged-proof/cycle/duplicate/outcome tests, SHA256 receipts, and read-only HTML. Recompute on source change, a new native run/attempt/job or owner receipt; do not rerun an unchanged failure solely because its color remains red.

\`N+1=N\` for one snapshot is not stability. At least **three consecutive complete, like-for-like and source-bound epochs** with no marginal new value, and no unowned unresolved obligation, are required to propose stopping that *lane*. A formal Six Sigma claim requires its own adequate statistical process population and variance assessment. Preserve \`HOLD\` on withheld gates.

### Runtime / artifacts

\`\`\`bash
python mission_control/mycelium/ops_dag/ops_dag.py \
 --input mission_control/mycelium/ops_dag/W33_SELECTED_OBSERVATIONS.json \
 --out /tmp/w33 --head <exact CODEX PR head>
python mission_control/mycelium/ops_dag/ops_dag.py \
 --input mission_control/mycelium/ops_dag/W33_SELECTED_OBSERVATIONS.json \
 --out /tmp/w33 --head <same head> --verify-only
\`\`\`

Outputs: \`W33_TASK_DAG.json\`, \`W33_TASK_METRICS.json\`, \`W33_SIPOC.json\`, \`W33_TASK_VIEWER.html\`, \`W33_SHA256.json\`. An optional \`--previous\` snapshot emits matched-population temporal deltas, never source coverage credit.

Security: no action buttons, credentials, external scripts, raw private artifacts, second source authority or remote mutation. The viewer uses textContent rather than rendering untrusted node labels as HTML.
