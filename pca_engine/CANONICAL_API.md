# `pca_engine` — CODEX Consumer API (Federation P1)

> **Status:** CODEX consumer and compatibility API; not the mathematical SSOT.
> **Provider:** `GBOGEB/gg_MATH/kernels/` (see `MATH_SSOT_BINDING.md`).
> Historical federation P1 docs promoted this API as canonical; that claim is
> superseded by the gg_MATH binding and ABACUS PR #2474.

This installable package provides compatible decision analytics for CODEX.
It has a local parity harness against the ABACUS TypeScript consumer.
That test does **not** establish parity with the gg_MATH provider, its
fail-closed Bradley–Terry admission semantics, or independent release approval.
Consumers must pin the provider SHA and preserve its DEFER decisions.

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

## CODEX consumer functions

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

The CODEX consumer engine and the ABACUS TS port implement the **same** Hunter (2004)
MM update. Two conventions differ and are **intentional** — the parity tests
assert both:

1. **Normalisation basis.** CODEX normalises strengths so the **arithmetic
   mean == 1**. ABACUS normalises so the **geometric mean == 1**. Ranking order
   and pairwise win-probabilities `pi/(pi+pj)` are invariant to either, so port
   those directly; do not compare raw strength magnitudes across engines.
2. **Prior / regularisation.** ABACUS adds a `prior = 0.1` pseudo-count to keep
   strengths finite on sparse data; canonical uses no prior and instead floors
   wins at `EPS`. Neither behavior proves a finite unregularized MLE.
   With the prior set to `0`, win-probabilities match to `1e-6`
   (verified in `test_win_probabilities_match_without_prior`). With the default
   prior, ABACUS win-probabilities are shrunk toward `0.5`
   (`test_default_prior_shrinks_toward_half`).

**Recommendation for spokes:** use gg_MATH for authoritative mathematical
ranking and reject its DEFER outcomes. `fit_bradley_terry` is a consumer helper
only. Do not promote EPS-regularized or prior-regularized results to a
finite-MLE PASS without the provider's admission and convergence proof.

## Scoped local parity guarantee

`tests/test_parity_spoke_stats.py` embeds a faithful Python port of the ABACUS
`bradleyTerry` and asserts: identical ranking order, win-probability agreement
with prior removed, documented shrinkage with the default prior, and the two
normalisation bases. If any assertion breaks, local parity has drifted and the
convergence plan must be revisited. The test does not cover gg_MATH's
Ford-condition DEFER guard or provide an owner/release acceptance. See
[consumer authority contract](CONSUMER_AUTHORITY_CONTRACT.md).
