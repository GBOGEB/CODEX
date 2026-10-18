# CODE PURPLE W36 — federated DoV / CBD! scalable expansion

**CODEX source-owner additive projection only.** Existing owners are ABACUS #1860, CODEX #977 and QPS; existing MYCELIUM W30/W31, W33 task DAG and W34 bounded scheduler are not replaced. `MERGE_ADMISSION=HOLD`, no new authenticated cross-repo dispatch, security waiver or assumed human approval.

## Immutable source and control boundary

- CODEX source base: `8361e6922f0768c66abcdd05c8ef865715cf048f` (already includes merged W31 #1106).
- ABACUS main observed at snapshot: `994ad6e73c748923841d92b12651e92d41b2d4ff`; current comparable global statement/branch coverage **UNKNOWN**.
- QPS private owner main metadata was observed as `fc07545c3986181a1b837c0eb7ff9a8393fd4058`, but no private QPS Actions/jobs or engineering contents are fetched into the public CODEX viewer.
- Published static source: `docs/data/code-purple-dov-w36.json` (frozen source receipt); responsive concentrated landing `docs/code-purple-dov.html`; added portal link `docs/index.html`. Source report is versioned and non-authoritative.
- Read-only GitHub refresh: HTML button calls only public GitHub API branches/main and first page of same-head runs for ABACUS/CODEX. It never inserts browser secrets, infers completed outcomes from queued records, or rewrites a frozen source ledger. New heads are new incomparable epochs.
- Automated emission: `.github/workflows/code-purple-dov-w36.yml` runs a **single** source-owned Ubuntu job on PR/dispatch and **daily** on main, with `actions:read`, `contents:read` and no write permissions, publishing `W36_LIVE_READBACK.json` plus `W36_SHA256.json` as one GitHub artifact. Collector limits **three API pages per public repo**, deduplicates workflow-run IDs and tracks observed/unknown tail; private QPS explicitly DEFER.

## Global DoV roll-up and separate clock metrics

| Layer | Native denominator / acceptance | Evidence state |
|---|---|---|
| Atomic | Source SHA, GitHub run/job/attempt, test IDs, hashes | W35 [B0 #39161525658](https://github.com/GBOGEB/ABACUS/actions/runs/39161525658): terminal; 5,006 passed, 3 skipped. Exact W35 matrix #39161525547: terminal success |
| Wave | Actual effect of candidate against original first-red | W35 earlier fail-fast 3 failed / 3,854 passed moved to candidate B0 terminal PASS. These cohorts differ in source and test population: no matched coverage credit |
| Family | Distinct root fingerprint, recurrence, behavioral/branch effect | W10 optional ZIP markers: shared first-red manifestations fixed in #2276 candidate; #2277 overlaps, reconcile before any additional source commit. Accepted owner closure UNKNOWN |
| Cluster | Independent owner producer→consumer proof | CODEX W30 four-cell native graph success; W31 native census success; W33 operational DAG success. QPS reciprocal readback UNKNOWN |
| Global | Independent security, rules, human review, main exact SHA, branch coverage | HOLD: no formal merger-admission, causal or global source-coverage credit |

Historical B0 `35,571/52,497=67.758%` is source-bound to `9e0200190555736c74295ee74881e3c003e8a35c`, not present-main coverage. W12 graph 37/46, W30 48/47, W33 task graph 20/17 count **different graph populations**; do not add them or call growth without matched selection.

## Queue pressure, segregation and misleading aggregation

Same ABACUS main SHA readbacks 86→103→133→172→196→612 are GitHub **run records** rather than terminal jobs, independent defects or equal-spaced times. The latest 612-run query fetched only the 100 newest; all 100 queued, unreturned **512**. The earlier *complete* 196-run cohort had **157 PR Feedback Gate Evaluator runs (80.1%)**, not evidence that 80.1% of all later 612 runs are in the same family. Keep distinct `runs/attempts/jobs`, event causes, source branches, native root fingerprints, queue p50/p95, and throughput per interval.

Metrics to establish in next wave:

1. **Coverage/denominator:** same-head+scope+coverage-config statement/branch ratio and exact changed-line coverage; track newly covered previously-uncovered branches and fault oracle effectiveness; do not reward new tests if effective behavior stays zero.
2. **Adversarial penetration:** independently effective fault-oracle pairs / eligible planned pairs; negative/reverse/ABA replay, stale SHA, artefact loss, forged header, no-test-zero guards and fail-closed security.
3. **Federation penetration:** verified paired producer+consumer run/job/attempt/artifact/hash / eligible cross-repo pairs; private QPS unknown until owner-supported return.
4. **Platform reach:** terminal proof per *distinct* OS/interpreter/family, with baseline and expanded JUnit+branch denominator; do not turn platform fixture successes into broad main uplift.
5. **Causal closure:** deduplicated roots accepted by owner / eligible distinct root candidates; first-red stage displacement, reopened defects and recurrence kept as independent metrics.
6. **Execution economics:** run amplification per event, unique workflow per PR/head, observed queue latency and p95, native proof yield per added runner-minute, failed→unblocked dependent transitions.

## Disjoint N+1 source-owner plan (proposal, not dispatch)

| Lane | Ownership | Bounded slice and negative proof | Gate |
|---|---|---|---|
| A | ABACUS B0/coverage | Reuse #2276 native; reconcile overlapping #2277; measure retained full test census, new branch arcs and mutation trip ratios | No CI gate weakening, no new duplicate B0 run |
| B | CODEX W36 dashboard/census | One Ubuntu native job; fail-closed 21 Python fixtures, inline JavaScript syntax, source-hashed artifact and tracked public pagination | Publication/browser QA are separate from native acceptance |
| C | ABACUS workflow trigger policy | Inspect repetitive PR Feedback Gate events and name/run/attempt/sha correlation. Propose idempotent trigger change only after source-owner attribution | Preserve required feedback and negative RED canary |
| D | QPS domain authority | Stage signed/source-bound export or explicit DEFER. CODEX projection never polls private jobs | QPS owner approval required |
| E | CODEX W33/W34 | Read existing task graph, queue and measured capacity, then evaluate qualified proposals per lane | No parallel scheduler, no unmeasured capacity assumption |

**Control/stopping rule:** measure at least four comparable observations yielding three consecutive matched deltas for each axis. If below target with flat marginal gain, redirect to disjoint eligible source, not a fabricated global plateau. A child PASS never compensates for governance or integration HOLD. Marginal gains are source/branch reach, verified negative fault response, native runner reach and genuine accepted root burndown—not merely graph nodes or queued tests.

## Commands

```bash
python -m unittest discover -s tests -p 'test_code_purple_dov_w36.py' -v
python scripts/code_purple_dov_census_w36.py --snapshot docs/data/code-purple-dov-w36.json --out w36_readonly --head <exact-candidate-sha>
python scripts/code_purple_dov_census_w36.py --snapshot docs/data/code-purple-dov-w36.json --out w36_readonly --head <exact-candidate-sha> --verify-only
```

## QA and release level

Static source/HTML/test code in the candidate branch is **IMPLEMENTED, NATIVE NOT YET VERIFIED** until terminal exact-head CI. Browser viewport, console, click and network-fallback Playwright checks are separate and must not be claimed PASS until executed. SHA256 and native tool receipts become `EXACT_SHA_RECEIPT` only when the new W36 job is terminal, artifact complete and hash verified. All other evidence is source-reported read-only. No release/merge action was requested or performed by this wave.
