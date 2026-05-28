"""[WAVE.W000] PCA drift monitor bootstrap.

Tracks drift between semantic and temporal layers using a minimal numerical
proxy that can be extended in W002.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class DriftSignal:
    """Container for drift computation output."""

    score: float
    stable: bool


def compute_drift_score(baseline: Iterable[float], observed: Iterable[float]) -> float:
    """Return mean absolute deviation between baseline and observed vectors."""
    baseline_list = list(baseline)
    observed_list = list(observed)
    if len(baseline_list) != len(observed_list):
        raise ValueError("baseline and observed vectors must have equal length")
    if not baseline_list:
        raise ValueError("input vectors must not be empty")
    deviation = [abs(a - b) for a, b in zip(baseline_list, observed_list)]
    return sum(deviation) / len(deviation)


def evaluate_drift(
    baseline: Iterable[float],
    observed: Iterable[float],
    threshold: float = 0.15,
) -> DriftSignal:
    """Evaluate drift score and classify stability against threshold."""
    score = compute_drift_score(baseline, observed)
    return DriftSignal(score=score, stable=score <= threshold)


if __name__ == "__main__":
    signal = evaluate_drift([0.9, 0.75, 0.4], [0.88, 0.71, 0.5])
    print({"score": round(signal.score, 4), "stable": signal.stable})
