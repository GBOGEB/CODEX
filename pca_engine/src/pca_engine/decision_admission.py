"""Fail-closed CODEX preflight for gg_MATH Bradley-Terry provider inputs.

This is a *necessary* admissibility test, not a Bradley-Terry fit and
not mathematical authority. GBOGEB/gg_MATH/kernels remains the provider.
"""
from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from typing import Any

PROVIDER = "GBOGEB/gg_MATH/kernels/bradley_terry.py"
DEFER_NO_USABLE_COMPARISONS = "DEFER_NO_USABLE_COMPARISONS"
DEFER_DISCONNECTED_COMPARISON_GRAPH = "DEFER_DISCONNECTED_COMPARISON_GRAPH"
DEFER_NO_FINITE_MLE = "DEFER_NO_FINITE_MLE"
DEFER_INVALID_COMPARISON = "DEFER_INVALID_COMPARISON"
DEFER_UNSUPPORTED_TIE = "DEFER_UNSUPPORTED_TIE"
ELIGIBLE_PROVIDER_PREFLIGHT = "BT_PREFLIGHT_ELIGIBLE"


def _reachable(start: str, edges: Mapping[str, set[str]]) -> set[str]:
    seen: set[str] = set()
    pending = [start]
    while pending:
        node = pending.pop()
        if node not in seen:
            seen.add(node)
            pending.extend(edges[node] - seen)
    return seen


def check_bt_admission(
    ids: Sequence[str], comparisons: Sequence[Mapping[str, Any]]
) -> dict[str, Any]:
    """Check provider edge/schema viability; never return strength or rank.

    The current gg_MATH rank_pairs accepts decisive winner/loser pairs, not
    pseudo-count or weighted tie rows. A pair is eligible only when both
    directions of the decisive win graph are reachable (Ford condition).
    """
    def receipt(status: str, count: int) -> dict[str, Any]:
        return {
            "status": status,
            "eligible": status == ELIGIBLE_PROVIDER_PREFLIGHT,
            "decisive_comparisons": count,
            "provider": PROVIDER,
            "authority": "CONSUMER_PREFLIGHT_ONLY",
        }

    if (
        not isinstance(ids, (list, tuple))
        or not isinstance(comparisons, (list, tuple))
        or len(ids) < 2
        or any(not isinstance(i, str) or not i for i in ids)
        or len(set(ids)) != len(ids)
    ):
        return receipt(DEFER_INVALID_COMPARISON, 0)

    allowed = set(ids)
    forward = {name: set() for name in ids}
    reverse = {name: set() for name in ids}
    undirected = {name: set() for name in ids}
    decisive = 0
    for row in comparisons:
        if not isinstance(row, Mapping):
            return receipt(DEFER_INVALID_COMPARISON, decisive)
        a, c = row.get("a"), row.get("b")
        if not isinstance(a, str) or not isinstance(c, str) or a not in allowed or c not in allowed or a == c:
            return receipt(DEFER_INVALID_COMPARISON, decisive)
        try:
            x, y = row["a_score"], row["b_score"]
            if any(type(v) not in (int, float) or not math.isfinite(v) for v in (x, y)):
                return receipt(DEFER_INVALID_COMPARISON, decisive)
        except (KeyError, TypeError):
            return receipt(DEFER_INVALID_COMPARISON, decisive)
        if x < 0 or y < 0 or abs((x + y) - 1) > 1e-9:
            return receipt(DEFER_INVALID_COMPARISON, decisive)
        if x not in (0, 1) or y not in (0, 1):
            return receipt(DEFER_UNSUPPORTED_TIE, decisive)
        winner, loser = (a, c) if x == 1 else (c, a)
        forward[winner].add(loser)
        reverse[loser].add(winner)
        undirected[winner].add(loser)
        undirected[loser].add(winner)
        decisive += 1
    if not decisive:
        return receipt(DEFER_NO_USABLE_COMPARISONS, 0)
    if len(_reachable(ids[0], undirected)) != len(ids):
        return receipt(DEFER_DISCONNECTED_COMPARISON_GRAPH, decisive)
    if len(_reachable(ids[0], forward)) != len(ids) or len(_reachable(ids[0], reverse)) != len(ids):
        return receipt(DEFER_NO_FINITE_MLE, decisive)
    return receipt(ELIGIBLE_PROVIDER_PREFLIGHT, decisive)
