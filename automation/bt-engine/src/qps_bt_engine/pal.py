from __future__ import annotations

WEIGHT_KEYS = ("reliability", "performance", "functional", "quality", "cost")


def normalized_score(requirement: dict, weights: dict[str, float]) -> float:
    """Return deterministic PAL score for one normalized requirement record."""
    if requirement.get("legal_mandate") or requirement.get("safety_mandate"):
        return 1_000_000.0
    scores = requirement.get("scores", {})
    return sum(float(scores.get(key, 0.0)) * float(weights.get(key, 0.0)) for key in WEIGHT_KEYS)


def compare_requirements(left: dict, right: dict, weights: dict[str, float], tie_threshold: float = 0.000001) -> float:
    """Return 1.0 when left wins, 0.0 when right wins, and 0.5 for tie."""
    left_score = normalized_score(left, weights)
    right_score = normalized_score(right, weights)
    delta = left_score - right_score
    if abs(delta) <= tie_threshold:
        return 0.5
    return 1.0 if delta > 0 else 0.0
