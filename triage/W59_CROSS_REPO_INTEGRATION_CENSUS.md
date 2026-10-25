# Cross-Repo Integration / Merge / Prune Triage — W59

**Scope:** `GBOGEB/ABACUS`, `GBOGEB/CODEX`, `GBOGEB/cryoplant-project`
**Author:** automated triage (GitHub integration as `gbogeb`)
**Date:** 2026-10-25
**Authority:** ANALYSIS / RECOMMENDATION ONLY — no merges executed; PRs opened for human review.

---

## 0. GitHub integration status

| Capability | State |
|---|---|
| Identity | Authenticated connector as **`gbogeb`** (admin/push/triage on all three repos) |
| Read (commits, trees, blobs, PRs) | Working on all three |
| Write (branch, file, PR) | Working — used to open this PR |
| Raw `git clone`/`git fetch` in build env | **Blocked** by environment guard — all repo work routed through the connector API |
| Local `c:/repos`, `c:/DEV` | **Not reachable** from the automation environment (owner's Windows machine) |
| Private-repo access for the Abacus app | Grant/extend via <https://github.com/apps/abacusai/installations/select_target> |

---

## 1. Repo inventory (live reads, 2026-10-25)

| Repo | Vis. | Primary lang | Tracked blobs | Last push | Open PRs |
|---|---|---|---|---|---|
| **cryoplant-project** | private | Python | ~7,741 | 2026-09-07 14:01 | **#628** W57 freeze QPS cADR/xOCD + TRIAGE views |
| **CODEX** | public | Python | ~2,779 | 2026-09-07 14:01 | none |
| **ABACUS** | private | Python (+ TSX app) | ~2,534* | 2026-09-06 (+bot 09-07) | **#926** W57 DOW cADR/xOCD + runtime view |

*ABACUS count is from a local checkout at `e986730` (2026-09-03); origin/main is ahead at W54-P12 (2026-09-06).

### File-type profile (blobs)

| Ext | cryoplant | CODEX | ABACUS |
|---|---|---|---|
| yaml/yml | 2,176 | 667 | 334 |
| py | 1,480 | 858 | 607 |
| json | 1,464 | 380 | 185 |
| md | 1,304 | 529 | 888 |
| html | 435 | 140 | 168 |
| tsx/ts | 30 | 18 | 96 |

Reading: cryoplant is **artifact-heavy** (generated triage receipts); CODEX is **code+governance balanced**; ABACUS is **doc-heavy** and uniquely carries the TSX web app (slide-reviewer).

---

## 2. Smoke posture (honest)

Python execution/smoke could **not** be run in the automation environment (external clone blocked; no Python runtime for these repos there). Structure-verifiable only:

| Repo | `tests/` files | CI | Note |
|---|---|---|---|
| cryoplant-project | ~249 | `.github/` present | large suite; not executed here |
| CODEX | ~260 | `.github/` present | `pca_engine/tests/` = 6 pytest modules |
| ABACUS | present | 90 workflows (metrics) | slide-reviewer app builds; Python suite not executed |

Only the ABACUS slide-reviewer web app is smoke-testable in the automation environment. The Python repos need smoke in their own CI / on a developer machine.

---

## 3. Shared-subsystem matrix (integration/drift map)

Counts = files under that top-level path per repo.

| Subsystem | cryoplant | CODEX | ABACUS | Observation |
|---|---|---|---|---|
| `federation/` | 60 | **203** | yes | Tri-present → **drift risk**; no single source of truth |
| `governance/` | 17 | **173** | yes | CODEX richest → hub candidate |
| `ssot/` | 7 | **62** | yes | Named "single source of truth" yet triplicated |
| `mission_control/` | 13 | **150** | – | CODEX-centred orchestration |
| `abacus_render_pipeline/` | – | 64 | yes | Duplicated ABACUS ↔ CODEX → dedupe |
| `pca_engine/` | – | **39** | – | **Canonical stats engine lives only in CODEX** |
| `triage/` | **5,349** | 80 | – | cryoplant = generated-artifact firehose |
| `OFFERS_ITT/` | 28 | – | yes | Offer-review artifacts split ABACUS ↔ cryoplant |
| `qcell_svg_model/` | – | 49 | yes | Duplicated ABACUS ↔ CODEX |
| `semantic_substrate/` | – | 43 | – | CODEX-only |

---

## 4. Integration / merge points (ranked)

### P1 — Canonicalize statistics on CODEX `pca_engine` (highest value)
The slide-reviewer (`ABACUS/qps_slide_reviewer/lib/stats.ts`) **re-implements** Bradley–Terry and PCA by hand (power-iteration PCA; Fisher-information std-error BT, which returns `Infinity` for un-compared items). CODEX `pca_engine` already provides stronger versions:

- `bradley_terry.py` → `fit_bradley_terry` (MM, 2000 iters, tolerance convergence) **and `bootstrap_bradley_terry`** (strength + rank CIs, `top_rank_probability`).
- `pca_core.py`, `pca_loadings.py`, `pca_metrics.py`, `pca_reconstruction.py`, `nlpca_autoencoder.py` — first-principles PCA (NumPy covariance/eigendecomposition), optional scikit-learn validation; CLI emits `summary.json/scores.csv/components.csv/loadings.csv/report.md`.
- Authority guard `PAIRWISE_DECISION_ANALYTICS_ONLY`, **BT kept independent of PCA** — also resolves the feature-leakage concern (slide-reviewer currently feeds BT-derived features back into PCA).

**Recommendation:** make `pca_engine` the single authority. Converge the slide-reviewer by either (a) exporting its item×feature matrix + comparisons to the `pca_engine` CLI/contract, or (b) porting `lib/stats.ts` to the `pca_engine` contract (MM + bootstrap CIs, BT⟂PCA) with documented parity. Stop maintaining two divergent implementations.

### P2 — `federation/` single source of truth
Present in all three with different sizes (60 / 203 / yes) → drift. Promote CODEX `federation/` to canonical; ABACUS + cryoplant consume it as a **git submodule** or published package.

### P3 — `governance/` + `ssot/` hub-and-spoke
CODEX holds the richest `governance/` (173) and `ssot/` (62). Designate CODEX the governance hub; others reference its SSOT instead of partial copies.

### P4 — dedupe `abacus_render_pipeline/` and `qcell_svg_model/`
Both duplicated ABACUS ↔ CODEX. Pick one owner and dedupe.

---

## 5. Prune points

| Target | Repo | Why | Action |
|---|---|---|---|
| `ABACUS-v031/`, `ABACUS-v032/`, `ABACUS_V21_DEPLOYMENT_PACKAGE/`, `DELTA_1/`, `DMAIC_V3_OUTPUT/`, `demo_workspace/` | ABACUS | Stale version snapshots / generated output in git; inflate repo, blur SSOT | Archive to a tag/release, then remove from `main` |
| `metrics: update DMAIC metrics ...` auto-commits **without `[skip ci]`** | ABACUS | CODEX's equivalent uses `[skip ci]`; ABACUS doubles commit count and re-triggers CI | Add `[skip ci]` to the metrics workflow |
| `triage/` (5,349 files) | cryoplant | Appears to be generated receipts in git | Evaluate artifact store / release assets; keep index in git |

---

## 6. Assimilation recommendation (alternative integration)

**Hub-and-spoke federation, not a monorepo.**

1. **CODEX = canonical hub** — owns `pca_engine`, `governance`, `ssot`, `federation`, `mission_control`.
2. **Publish `pca_engine`** as an installable internal package (already has `pyproject.toml` + CLI + tests) consumed by cryoplant analyses, ABACUS DOW-PCA, and the slide-reviewer (via its contract).
3. **`federation/` + `ssot/` as submodules** pinned from CODEX into ABACUS and cryoplant — one source, pinned SHAs, no drift.
4. **ABACUS = application + offer-review surface**; **cryoplant = domain execution/triage**; both reference CODEX rather than copying it.
5. **Prune** stale snapshots and apply `[skip ci]` consistently.

Preserves the wave cadence while removing the three-way duplication that makes "single source of truth" untrue today.

---

## 7. PR plan

| PR | Repo | Status | Content |
|---|---|---|---|
| This triage | **CODEX** | **opened** | This document under `triage/` |
| ABACUS `[skip ci]` metrics fix | ABACUS | needs go-ahead | Add `[skip ci]` to the DMAIC metrics auto-commit |
| Slide-reviewer ⟶ `pca_engine` convergence | ABACUS | needs decision | Export-to-CLI vs port `lib/stats.ts` to the `pca_engine` contract |
| `federation/` submodule SSOT | ABACUS + cryoplant | needs decision | Promote CODEX `federation/` to canonical + submodule the spokes |

Merges are **not** performed automatically — open PRs (#628 cryoplant, #926 ABACUS) and the above remain for review.
