"""Parity harness: canonical ``pca_engine`` vs. spoke re-implementations.

Federation action **P1** (see ``GBOGEB/ABACUS:docs/INTEGRATION_REPORT.md``): the
Bradley-Terry + PCA statistics must be single-sourced on this ``pca_engine`` package.
ABACUS currently hand-rolls the same maths in
``qps_slide_reviewer/lib/stats.ts``. This test encodes a faithful Python port of
that TypeScript implementation and compares it against the canonical functions so
that any numerical divergence is *explicit and tracked* rather than silently
assumed to match.

Documented divergences (as of this pass) -- these are intentional and asserted
below, not bugs:

* **Normalisation basis.** Canonical ``fit_bradley_terry`` normalises strengths so
  the *arithmetic* mean == 1. The ABACUS port normalises so the *geometric* mean
  == 1. Ranking order and pairwise win-probabilities ``pi/(pi+pj)`` are invariant
  to either scaling, so those are compared directly.
* **Prior / regularisation.** The ABACUS port adds a ``prior = 0.1`` pseudo-count
  (a pseudo-comparison vs. a strength-1 opponent) to keep strengths finite on
  sparse data; canonical uses no prior. With the prior set to ``0.0`` the two
  implementations agree to tolerance; with the ABACUS default prior they agree on
  *ranking order* but win-probabilities are slightly shrunk toward 0.5. Both
  behaviours are asserted so the regularisation gap is pinned.

If a future change breaks one of these assertions, parity has drifted and the
convergence plan must be revisited.
"""
from __future__ import annotations

import math
from typing import Any, Sequence

import numpy as np
import pytest

from pca_engine import fit_bradley_terry, comparisons_from_utilities


# --------------------------------------------------------------------------- #
# Faithful Python port of ABACUS qps_slide_reviewer/lib/stats.ts::bradleyTerry
# --------------------------------------------------------------------------- #
def abacus_bradley_terry(
    ids: Sequence[Any],
    comparisons: Sequence[dict[str, Any]],
    *,
    iterations: int = 200,
    prior: float = 0.1,
) -> dict[Any, float]:
    """Port of the ABACUS TS MM algorithm (Hunter 2004) with a small prior.

    ``comparisons`` uses the same ``{a, b, a_score, b_score}`` shape as the
    canonical engine so a single fixture drives both sides. ``a_score``/``b_score``
    are the fractional wins for ``a``/``b`` (tie -> 0.5/0.5), matching how the TS
    code accumulates ``wij``.
    Returns strengths normalised so the geometric mean == 1 (as the TS code does).
    """
    names = [str(x) for x in ids]
    n = len(names)
    index = {name: i for i, name in enumerate(names)}
    nij = [[0.0] * n for _ in range(n)]
    wij = [[0.0] * n for _ in range(n)]
    for row in comparisons:
        a, b = str(row["a"]), str(row["b"])
        ia, ib = index[a], index[b]
        a_score, b_score = float(row["a_score"]), float(row["b_score"])
        wij[ia][ib] += a_score
        wij[ib][ia] += b_score
        nij[ia][ib] += 1.0
        nij[ib][ia] += 1.0

    pi = [1.0] * n
    for _ in range(iterations):
        nxt = [0.0] * n
        for i in range(n):
            W = prior
            denom = 0.0
            for j in range(n):
                if i == j:
                    continue
                W += wij[i][j]
                if nij[i][j] > 0:
                    denom += nij[i][j] / (pi[i] + pi[j])
            denom += prior * 2.0 / (pi[i] + 1.0)
            nxt[i] = W / denom if denom else 0.0
        # geometric-mean normalisation (exactly as the TS code)
        gm = math.exp(sum(math.log(v) for v in nxt) / n)
        pi = [v / gm for v in nxt]
    return {names[i]: pi[i] for i in range(n)}


def _win_prob(strengths: dict[Any, float], a: str, b: str) -> float:
    sa, sb = strengths[a], strengths[b]
    return sa / (sa + sb)


# --------------------------------------------------------------------------- #
# Fixtures: shared comparison sets driving both implementations
# --------------------------------------------------------------------------- #
@pytest.fixture
def four_item_utilities() -> dict[str, float]:
    return {"alpha": 4.0, "beta": 3.0, "gamma": 2.0, "delta": 1.0}


@pytest.fixture
def comparisons(four_item_utilities):
    # deterministic pairwise basis -> clear transitive ordering
    return comparisons_from_utilities(four_item_utilities)


@pytest.fixture
def nondegenerate_comparisons(four_item_utilities):
    """A non-degenerate set where EVERY item wins at least once.

    A perfect total order leaves the weakest item with zero wins, which makes an
    unregularised MM fit collapse its strength to 0 (``log(0)``). That degenerate
    case is precisely why the ABACUS port carries a prior; to compare the *update
    rule itself* (prior removed) we add two upsets so no strength vanishes.
    """
    rows = comparisons_from_utilities(four_item_utilities)
    rows = [dict(r) for r in rows]
    # upsets: delta beats alpha, gamma beats beta
    rows.append({"a": "delta", "b": "alpha", "a_score": 1.0, "b_score": 0.0})
    rows.append({"a": "gamma", "b": "beta", "a_score": 1.0, "b_score": 0.0})
    return rows


# --------------------------------------------------------------------------- #
# Tests
# --------------------------------------------------------------------------- #
def test_ranking_order_matches(four_item_utilities, comparisons):
    """Both implementations must produce the SAME ranking order."""
    ids = list(four_item_utilities)
    canonical = fit_bradley_terry(ids, comparisons)
    abacus = abacus_bradley_terry(ids, comparisons)
    canonical_rank = canonical["ranking"]
    abacus_rank = sorted(ids, key=lambda k: abacus[k], reverse=True)
    assert canonical_rank == abacus_rank == ["alpha", "beta", "gamma", "delta"]


def test_win_probabilities_match_without_prior(four_item_utilities, nondegenerate_comparisons):
    """With the ABACUS prior disabled, pairwise win-probabilities agree to tol.

    This pins the claim that the two engines implement the *same* MM update; the
    only numerical difference is the regularisation prior. Uses the non-degenerate
    fixture so neither unregularised fit collapses a strength to zero.
    """
    ids = list(four_item_utilities)
    canonical = fit_bradley_terry(ids, nondegenerate_comparisons)["strengths"]
    abacus = abacus_bradley_terry(ids, nondegenerate_comparisons, prior=0.0)
    for i, a in enumerate(ids):
        for b in ids[i + 1:]:
            p_can = _win_prob(canonical, a, b)
            p_aba = _win_prob(abacus, a, b)
            assert p_can == pytest.approx(p_aba, abs=1e-6), (
                f"win-prob divergence for {a} vs {b}: canonical={p_can} abacus={p_aba}"
            )


def test_default_prior_shrinks_toward_half(four_item_utilities, comparisons):
    """The ABACUS default prior=0.1 must shrink win-probabilities toward 0.5.

    Documents the intentional regularisation divergence: same ranking, softer
    probabilities than the unregularised canonical engine.
    """
    ids = list(four_item_utilities)
    canonical = fit_bradley_terry(ids, comparisons)["strengths"]
    abacus = abacus_bradley_terry(ids, comparisons, prior=0.1)
    # strongest vs weakest: canonical is more extreme than the regularised port
    p_can = _win_prob(canonical, "alpha", "delta")
    p_aba = _win_prob(abacus, "alpha", "delta")
    assert p_can > p_aba > 0.5, (p_can, p_aba)


def test_strengths_positive_and_normalised(four_item_utilities, comparisons):
    """Canonical: arithmetic mean == 1. ABACUS port: geometric mean == 1."""
    ids = list(four_item_utilities)
    canonical = fit_bradley_terry(ids, comparisons)["strengths"]
    abacus = abacus_bradley_terry(ids, comparisons)
    assert all(v > 0 for v in canonical.values())
    assert all(v > 0 for v in abacus.values())
    assert np.mean(list(canonical.values())) == pytest.approx(1.0, abs=1e-6)
    geo = math.exp(np.mean([math.log(v) for v in abacus.values()]))
    assert geo == pytest.approx(1.0, abs=1e-6)
