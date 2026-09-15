# ABACUS A10 / A9.3 — Lossless Session Handover

Date: 2026-09-15
Repository: `GBOGEB/CODEX`
Transaction PR: `#729`
Branch: `handover/a10-a9-3pr-mip-20260915`
Base main at transaction start: `19c8d094587c89bd5a24d7f0b34a38da39bf46ee`
Control ledgers after this transaction: `A10.2`

## 1. Session result

This session did **not** reopen the A10 snapshot renderer. It performed a full 3PR state refresh after the earlier A10 closure and found that repository truth had advanced:

- A10 snapshot publication remains independently proven and `DEBT-008 snapshot_receipt` remains `CLOSED`.
- A9 multi-format hosted publication is **not currently closed**. It is `DEBT-007 = PARTIAL` after a later burn-in and A9.3 exact-main failure exposed a hosted GitHub Pages repeatability/ownership problem.
- The first structural red is now a repository-wide Pages deployment ownership defect: one `deploy-pages` workflow was outside the shared `pages` concurrency boundary.
- PR #729 implements the bounded MIP repair and adds a recurrence guard, but it **must not** re-close DEBT-007 from PR-head evidence.

The controlling distinction is:

`A10 SNAPSHOT DOV != A9 HOSTED-PAGES STABILITY DOV`

A failure in the latter does not erase the former, and a pass in the former cannot compensate for the latter.

## 2. Canonical authority / read order

On restart, use repository truth in this order:

1. `abacus_render_pipeline/A7_executable_semantic_runtime/data/governance_ledger.json`
2. `abacus_render_pipeline/A7_executable_semantic_runtime/data/semantic_tuple_ledger.json`
3. `abacus_render_pipeline/A10_snapshot_publication/handover/MIP_RECEIPT_2026-09-15.yaml`
4. `abacus_render_pipeline/A10_snapshot_publication/handover/SESSION_HANDOVER_2026-09-15.md`
5. `abacus_render_pipeline/A10_snapshot_publication/handover/DROP_IN_CONTINUATION_2026-09-15.md`
6. `abacus_render_pipeline/A10_snapshot_publication/handover/SESSION_PROGRESS_LEDGER_2026-09-15.yaml`
7. only then inspect current Actions / PR state and execute the first-red.

Generated PNG/PPTX/PDF/HTML/Markdown outputs remain non-canonical. Execution receipts and source ledgers govern publication state.

## 3. A10 state — preserve, do not reopen without a concrete defect

A10 closure lineage:

- PR: `#698`
- merge commit: `7006236938ac3d7d7e8539e6b492ca532a41346b`
- post-merge exact-main workflow: `ABACUS Snapshot Publication`, run `34869064881`
- result: `PASS`
- image-native execution included real Chromium PNG generation, independent hash validation, dimensions, clipping, viewport overflow, text visibility, contrast, element coverage, semantic parity, replay, tamper rejection and promotion logic.

Known A10 evidence from the exact-main proof:

- PNG: `1440 x 1200`
- bytes: `99,471`
- Chromium: `140.0.7339.16`
- clipped elements: `0`
- horizontal overflow: `false`
- visible text elements: `63`
- hidden text elements: `0`
- minimum contrast ratio: `21.0`
- contrast failures: `0`
- element coverage: `1.0`
- missing semantic tokens: `0`
- snapshot decision: `accept`
- six-surface decision at that proof point: `PROMOTE`
- snapshot SHA-256: `5cd0d27c76b2f1b4b5a7a200a81a43ac57de0160586eb3d350f203b9690f7572`

Current governance interpretation:

- `INV-009` remains valid.
- `DEBT-008 = CLOSED` remains valid.
- `TUP-0013` remains a valid snapshot-publication lineage node.
- later GitHub Pages root propagation failures are a different evidence lane.

Do not spend another pulse on A10 unless a real visual-renderer defect or stronger snapshot-authority requirement appears.

## 4. A9 hosted Pages state — current active frontier

### 4.1 Earlier valid hosted proof

A9 had a valid historical hosted proof on exact main:

- source: `ed641574dedcf4f062ad333e07ef79d19388f3eb`
- run: `34867675282`
- hosted hash equality: PASS
- semantic coverage: `1.0`
- atomic publication decision: `PROMOTE`

That proof remains historical evidence, but it cannot compensate for a newer repeatability failure.

### 4.2 Burn-in regression that reopened DEBT-007

Later burn-in run `34868367167` showed:

- local deterministic candidates: PASS
- deploy-pages signal: success
- public endpoint: HTTP 200
- governed candidate SHA-256: `6737e566b54b907cf54d53dd91160ccb4d09aba3e34fba2035a1bae0eb90214c`
- hosted SHA-256: `39a754786ab9c2108d84d68fb29194901f5000032aea6d31f9326bf497acdefc`
- semantic coverage: `0.0`
- hosted receipt: reject

That correctly moved:

- `DEBT-007`: CLOSED -> PARTIAL
- `TUP-0012`: complete -> active_stability_gate

### 4.3 A9.3 repair and exact-main result

PR `#701` added A9.3 stable-convergence logic and merged as:

`6a9cf37718c945dc132d4ce58bea999dc3aa6b01`

A9.3 exact-main workflow run:

`34870534075`

Candidate job result:

- semantic vocabulary: PASS
- PPTX/PDF regression: PASS
- HTML/PPTX/PDF/Markdown/Pages candidates: PASS
- independent artifact hash/parity validation: PASS
- pre-hosted atomic decision: correctly WITHHOLD
- A9.3 tamper and hosted-receipt tests: PASS
- semantic closed loop / replay: PASS

Deployment job result:

- `actions/deploy-pages@v4`: SUCCESS
- Pages deployment reported success
- hosted proof: FAILURE
- attempts: `24`
- public endpoint stayed on SHA `39a754786ab9c2108d84d68fb29194901f5000032aea6d31f9326bf497acdefc`
- expected governed SHA `6737e566b54b907cf54d53dd91160ccb4d09aba3e34fba2035a1bae0eb90214c`
- semantic coverage remained `0.0`
- atomic PROMOTE step was skipped

This is a useful fail-closed outcome. It proves the remaining problem is outside local candidate generation and inside hosted endpoint ownership/propagation.

## 5. Full 3PR receipt

The current canonical 3PR meaning is `Refresh / Probe / Rank` and is repeated only after material state/evidence changes.

### P1 — Refresh

Refreshed:

- current `main` rather than relying on the earlier A10 close message;
- A7 governance and tuple ledgers;
- PR #698 / A10 exact-main evidence;
- PR #701 / A9.3 exact-main evidence;
- current Pages-deployment workflows.

Refresh result:

- A10 remains closed.
- A9 DEBT-007 is PARTIAL.
- the previous statement that there was no remaining publication-format gap is no longer sufficient as a total publication-state statement because hosted root stability regressed after A10.

### P2 — Probe

Probed the A9.3 failed exact-main run and the repository Pages deployment topology.

`actions/deploy-pages@v4` census at transaction start:

| Workflow | Publishes Pages | Shared `pages` concurrency before MIP |
|---|---:|---:|
| `.github/workflows/deploy_pipeline.yml` | yes | yes |
| `.github/workflows/pages.yml` | yes | yes |
| `.github/workflows/abacus-multiformat-publication.yml` | yes | yes |
| `.github/workflows/pages_deploy_runtime.yml` | yes | **no** |

Therefore A9.3 could hold its own `pages` lock while another deployer remained outside that lock and could modify the same public root.

### P3 — Rank

Ranked first-reds:

1. **PAGES-OWNERSHIP-001 — P0 / structural recurrence gap**
   - one deploy-pages workflow outside the repository-wide shared concurrency boundary;
   - must be repaired and made machine-auditable.
2. **A9-HOSTED-DOV-001 — P0 / execution proof**
   - after the ownership repair merges, exact-main A9.3 must prove stable hosted convergence and atomic PROMOTE.
3. Remaining A6/A7 debts (renderer lint integration, unified WCAG receipt evidence, semantic spacing, figure registry, semantic metrics) stay downstream and must not distract from the first-red.

A10 snapshot work is **not** ranked as an active red.

## 6. Full MIP receipt

MIP is admitted because the 3PR probe found a genuine structural/recurrence gap.

### Modernize

PR #729 changes `.github/workflows/pages_deploy_runtime.yml` so it joins:

```yaml
concurrency:
  group: pages
  cancel-in-progress: false
```

This aligns it with the other root Pages deployment lanes and makes A9.3's held concurrency boundary meaningful across all currently known deployers.

### Innovate

Added:

- `scripts/check_pages_deploy_concurrency.py`
- `tests/test_pages_deploy_concurrency.py`

The audit scans repository workflows that actually contain `actions/deploy-pages@v4` and rejects any deploy job for which neither workflow-level nor job-level concurrency binds to group `pages`.

A9 candidate preflight now executes both the audit and its regression test before renderer execution.

This does **not** claim that concurrency alone proves public CDN convergence. It proves only the repository-side shared deployment ownership predicate.

### Perpetuate

Persistent controls added/refreshed:

- `INV-011`: every root Pages deployer must participate in the shared `pages` boundary;
- `TUP-0014`: records this 3PR/MIP control transaction;
- `DEBT-007`: sharpened with exact A9.3 failure evidence and the post-MIP re-close predicate;
- `DEBT-008`: stays CLOSED;
- canonical full handover, drop-in and progress/MIP receipt surfaces are created for restart without chat memory.

## 7. Non-compensating rules

The following are mandatory:

- `DEPLOY-PAGES SUCCESS != HOSTED GOVERNED CONTENT`
- `HTTP 200 != HASH PARITY`
- `A10 SNAPSHOT PASS != A9 HOSTED PAGES PASS`
- `HISTORICAL A9 PROMOTE != CURRENT A9 REPEATABILITY`
- `CONCURRENCY TOPOLOGY PASS != HOSTED CONVERGENCE PASS`
- `PR-HEAD PASS != EXACT-MAIN HOSTED DOV`
- local HTML/PPTX/PDF/Markdown parity cannot compensate for a hosted root mismatch;
- a newer exact-main failure cannot be compensated by an older exact-main success;
- do not weaken the hosted predicate to obtain a green build.

## 8. PR #729 exact-head DoD

Before merge, require the exact PR head to prove at minimum:

1. repository Pages deployment concurrency audit PASS;
2. regression test PASS;
3. semantic vocabulary PASS;
4. A9 candidate lane PASS;
5. pre-hosted publication decision remains WITHHOLD on PR events;
6. semantic closed-loop and replay PASS through TUP-0014;
7. governance admission PASS;
8. no regression to A10 snapshot lineage or DEBT-008 closure.

Because production Pages deployment is push-on-main only, PR #729 cannot itself re-close DEBT-007.

## 9. Post-merge exact-main DoV / re-close predicate

After PR #729 merges, the next admissible closure proof is the resulting exact-main A9.3 push run.

Required sequence:

```text
candidate render/parity PASS
-> Pages deployment PASS
-> hosted response exact governed hash + semantic parity
-> second consecutive exact governed response
-> independent repeated two-match convergence
-> atomic PROMOTE
```

Only if all of the above pass may a bounded closure writeback:

- set `DEBT-007 = CLOSED`;
- set `TUP-0012 = complete`;
- record exact main SHA, run ID, hosted receipt SHA/artifact digest and promotion decision;
- leave `DEBT-008` unchanged as CLOSED.

If exact-main still fails after the concurrency repair:

- keep `DEBT-007 = PARTIAL`;
- inspect remaining root Pages ownership, deployment/environment behavior, or external Pages/CDN propagation;
- do not create a second publication architecture;
- do not reduce required match count or remove semantic/hash checks.

## 10. Canonical restart sequence

A fresh session should execute exactly this sequence:

```text
1. read current main ref
2. read governance_ledger.json
3. read semantic_tuple_ledger.json
4. read MIP_RECEIPT_2026-09-15.yaml
5. read SESSION_HANDOVER_2026-09-15.md
6. read DROP_IN_CONTINUATION_2026-09-15.md
7. inspect PR #729 state / merge receipt
8. if merged: locate exact-main ABACUS Multi-Format Publication run caused by the merge
9. inspect candidate job and deploy-and-prove-pages job
10. ACCEPT closure only on stable hosted convergence + atomic PROMOTE
11. otherwise preserve PARTIAL and execute the first observed red
12. refresh the same handover surfaces only on a material state/evidence change
```

## 11. Files changed by this transaction

Structural MIP:

- `.github/workflows/pages_deploy_runtime.yml`
- `.github/workflows/abacus-multiformat-publication.yml`
- `scripts/check_pages_deploy_concurrency.py`
- `tests/test_pages_deploy_concurrency.py`

Governed state:

- `abacus_render_pipeline/A7_executable_semantic_runtime/data/governance_ledger.json`
- `abacus_render_pipeline/A7_executable_semantic_runtime/data/semantic_tuple_ledger.json`

Lossless continuation:

- `abacus_render_pipeline/A10_snapshot_publication/handover/MIP_RECEIPT_2026-09-15.yaml`
- `abacus_render_pipeline/A10_snapshot_publication/handover/SESSION_HANDOVER_2026-09-15.md`
- `abacus_render_pipeline/A10_snapshot_publication/handover/DROP_IN_CONTINUATION_2026-09-15.md`
- `abacus_render_pipeline/A10_snapshot_publication/handover/SESSION_PROGRESS_LEDGER_2026-09-15.yaml`

## 12. Current victory / stop condition

This session's victory is **not** `DEBT-007 CLOSED`.

The current bounded victory is:

`3PR COMPLETE + MIP STRUCTURAL REPAIR MATERIALIZED + LOSSLESS HANDOVER MATERIALIZED + PR-HEAD VALIDATION`

The next transaction is admitted only by exact-main evidence after merge.

If exact-main A9.3 reaches atomic PROMOTE, perform one bounded evidence-binding closure writeback and STOP.
If it does not, continue only from the concrete hosted first-red and keep A10 closed.
