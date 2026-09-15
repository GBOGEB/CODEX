"""Generic Bradley-Terry pairwise ranking with bootstrap uncertainty.

This module is independent of PCA by design.  Callers may use PCA and reverse
pressure to understand structure, but those scores are not injected here.
"""
from __future__ import annotations

from typing import Any, Iterable, Sequence

import numpy as np

EPS = 1.0e-12


def _validate(ids: Sequence[str], comparisons: Sequence[dict[str, Any]]) -> list[str]:
    names = [str(x) for x in ids]
    if len(names) < 2 or len(set(names)) != len(names):
        raise ValueError("ids must contain at least two unique items")
    allowed = set(names)
    for row in comparisons:
        a, b = str(row.get("a")), str(row.get("b"))
        if a == b or a not in allowed or b not in allowed:
            raise ValueError("each comparison must reference two distinct known ids")
        a_score = float(row.get("a_score"))
        b_score = float(row.get("b_score"))
        if not np.isfinite([a_score, b_score]).all() or a_score < 0 or b_score < 0:
            raise ValueError("comparison scores must be finite and non-negative")
        if abs((a_score + b_score) - 1.0) > 1.0e-9:
            raise ValueError("a_score + b_score must equal 1")
    if not comparisons:
        raise ValueError("at least one comparison is required")
    return names


def fit_bradley_terry(
    ids: Sequence[str],
    comparisons: Sequence[dict[str, Any]],
    *,
    iterations: int = 2000,
    tolerance: float = 1.0e-11,
) -> dict[str, Any]:
    """Fit positive item strengths using the MM update for Bradley-Terry."""
    names = _validate(ids, comparisons)
    ability = {name: 1.0 for name in names}
    wins = {name: 0.0 for name in names}
    counts: dict[tuple[str, str], float] = {}
    for row in comparisons:
        a, b = str(row["a"]), str(row["b"])
        wins[a] += float(row["a_score"])
        wins[b] += float(row["b_score"])
        key = tuple(sorted((a, b)))
        counts[key] = counts.get(key, 0.0) + 1.0

    converged = False
    for iteration in range(1, iterations + 1):
        updated: dict[str, float] = {}
        for i in names:
            denominator = 0.0
            for j in names:
                if i == j:
                    continue
                nij = counts.get(tuple(sorted((i, j))), 0.0)
                if nij:
                    denominator += nij / max(ability[i] + ability[j], EPS)
            updated[i] = max(wins[i], EPS) / max(denominator, EPS)
        scale = sum(updated.values()) / len(updated)
        updated = {key: value / max(scale, EPS) for key, value in updated.items()}
        delta = max(abs(updated[key] - ability[key]) for key in names)
        ability = updated
        if delta < tolerance:
            converged = True
            break

    ranking = sorted(names, key=lambda name: ability[name], reverse=True)
    probabilities = {
        a: {b: (0.5 if a == b else ability[a] / (ability[a] + ability[b])) for b in names}
        for a in names
    }
    return {
        "strengths": ability,
        "ranking": ranking,
        "pairwise_win_probability": probabilities,
        "iterations": iteration,
        "converged": converged,
        "authority": "PAIRWISE_DECISION_ANALYTICS_ONLY",
        "guard": "independent of PCA and subject to caller execution/evidence gates",
    }


def bootstrap_bradley_terry(
    ids: Sequence[str],
    comparisons: Sequence[dict[str, Any]],
    *,
    confidence: float = 0.95,
    bootstrap_samples: int = 1000,
    seed: int = 0,
) -> dict[str, Any]:
    """Bootstrap strength and rank uncertainty by resampling pairwise observations."""
    names = _validate(ids, comparisons)
    if not 0.0 < confidence < 1.0:
        raise ValueError("confidence must be in (0,1)")
    if bootstrap_samples < 200:
        raise ValueError("bootstrap_samples must be >= 200")
    rng = np.random.default_rng(seed)
    rows = list(comparisons)
    strengths = {name: [] for name in names}
    ranks = {name: [] for name in names}
    for _ in range(bootstrap_samples):
        indices = rng.integers(0, len(rows), size=len(rows))
        sample = [rows[int(i)] for i in indices]
        fit = fit_bradley_terry(names, sample)
        for position, name in enumerate(fit["ranking"], start=1):
            ranks[name].append(position)
        for name in names:
            strengths[name].append(float(fit["strengths"][name]))
    alpha = 1.0 - confidence
    summary: dict[str, Any] = {}
    for name in names:
        s = np.asarray(strengths[name], dtype=float)
        r = np.asarray(ranks[name], dtype=float)
        slo, shi = np.quantile(s, [alpha / 2.0, 1.0 - alpha / 2.0])
        rlo, rhi = np.quantile(r, [alpha / 2.0, 1.0 - alpha / 2.0])
        summary[name] = {
            "strength_mean": float(s.mean()),
            "strength_lower": float(slo),
            "strength_upper": float(shi),
            "rank_median": float(np.median(r)),
            "rank_lower": float(rlo),
            "rank_upper": float(rhi),
            "top_rank_probability": float(np.mean(r == 1.0)),
        }
    return {
        "confidence_level": confidence,
        "bootstrap_samples": bootstrap_samples,
        "items": summary,
        "authority": "PAIRWISE_DECISION_ANALYTICS_ONLY",
    }


def comparisons_from_utilities(utilities: dict[str, float], *, tie_epsilon: float = 0.0) -> list[dict[str, Any]]:
    """Create explicit deterministic pairwise outcomes from declared utilities.

    This helper does not make the utilities authoritative; it simply exposes the
    exact pairwise basis used to fit a Bradley-Terry ranking.
    """
    names = list(utilities)
    if len(names) < 2 or not all(np.isfinite(float(v)) for v in utilities.values()):
        raise ValueError("at least two finite utilities are required")
    result: list[dict[str, Any]] = []
    for i, a in enumerate(names):
        for b in names[i + 1 :]:
            delta = float(utilities[a]) - float(utilities[b])
            if abs(delta) <= tie_epsilon:
                a_score, b_score = 0.5, 0.5
            elif delta > 0:
                a_score, b_score = 1.0, 0.0
            else:
                a_score, b_score = 0.0, 1.0
            result.append({"a": a, "b": b, "a_score": a_score, "b_score": b_score, "utility_delta": delta})
    return result
