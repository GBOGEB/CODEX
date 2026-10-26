# `pca_engine` — Canonical Statistics API (Federation P1)

> **Status:** canonical, single source of truth for Bradley-Terry ranking and
> PCA/NLPCA across the GBOGEB federation (CODEX hub · ABACUS runtime ·
> cryoplant-project child). See `GBOGEB/ABACUS:docs/INTEGRATION_REPORT.md` §4
> item 1 (action **P1**).

This package is the **only tested implementation** of the federation's shared
statistics. Spokes (ABACUS `qps_slide_reviewer/lib/stats.ts`, cryoplant parallel
paths) should converge onto these functions rather than maintain divergent copies.
Parity with the ABACUS re-implementation is pinned by
`tests/test_parity_spoke_stats.py`.

## Install / consume

```bash
pip install -e .            # from pca_engine/
# or build a wheel for spokes:
python -m build             # produces dist/gbogeb_pca_engine-*.whl
```

```python
from pca_engine import (
    fit_bradley_terry, bootstrap_bradley_terry, comparisons_from_utilities,
    fit_pca, transform, inverse_transform, PCAResult,
)
```

A CLI entry point is also exposed: `pca-engine` (see `pca_engine.cli:main`).

## Canonical functions

| Domain | Function | Purpose |
|--------|----------|---------|
| Bradley-Terry | `fit_bradley_terry(ids, comparisons, *, iterations=2000, tolerance=1e-11)` | MM fit of positive item strengths + ranking + pairwise win probabilities |
| Bradley-Terry | `bootstrap_bradley_terry(ids, comparisons, *, confidence=0.95, bootstrap_samples>=200, seed=0)` | Bootstrap strength & rank confidence intervals |
| Bradley-Terry | `comparisons_from_utilities(utilities, *, tie_epsilon=0.0)` | Deterministic pairwise basis from declared utilities |
| PCA | `fit_pca`, `transform`, `inverse_transform`, `PCAResult` | Core PCA on a standardised numeric matrix |
| PCA | `loadings`, `communality`, `top_features`, `cumulative_variance`, `reconstruct`, `reconstruction_metrics` | Loadings, variance & reconstruction diagnostics |

### `comparisons` schema

Each comparison is a dict: `{"a": id, "b": id, "a_score": float, "b_score": float}`
where `a_score + b_score == 1` (a tie is `0.5 / 0.5`), scores finite and
non-negative, and `a != b`.

## Numerical conventions (read before porting)

The canonical engine and the ABACUS TS port implement the **same** Hunter (2004)
MM update. Two conventions differ and are **intentional** — the parity tests
assert both:

1. **Normalisation basis.** Canonical normalises strengths so the **arithmetic
   mean == 1**. ABACUS normalises so the **geometric mean == 1**. Ranking order
   and pairwise win-probabilities `pi/(pi+pj)` are invariant to either, so port
   those directly; do not compare raw strength magnitudes across engines.
2. **Prior / regularisation.** ABACUS adds a `prior = 0.1` pseudo-count to keep
   strengths finite on sparse data; canonical uses no prior and instead floors
   wins at `EPS`. With the prior set to `0`, win-probabilities match to `1e-6`
   (verified in `test_win_probabilities_match_without_prior`). With the default
   prior, ABACUS win-probabilities are shrunk toward `0.5`
   (`test_default_prior_shrinks_toward_half`).

**Recommendation for spokes:** call `fit_bradley_terry` directly. If the ABACUS
regularisation behaviour is required, expose a `prior`/`alpha` option on a thin
wrapper rather than re-deriving the MM loop.

## Parity guarantee

`tests/test_parity_spoke_stats.py` embeds a faithful Python port of the ABACUS
`bradleyTerry` and asserts: identical ranking order, win-probability agreement
with prior removed, documented shrinkage with the default prior, and the two
normalisation bases. If any assertion breaks, parity has drifted and the
convergence plan must be revisited before a spoke is retired.
