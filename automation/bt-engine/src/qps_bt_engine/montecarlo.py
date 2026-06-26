from __future__ import annotations

import random
from dataclasses import dataclass
from statistics import mean


@dataclass(frozen=True)
class MonteCarloConfig:
    iterations: int = 1000
    weight_tolerance: float = 0.05
    seed: int = 42


def perturb_weights(weights: dict[str, float], rng: random.Random, tolerance: float) -> dict[str, float]:
    out = {}
    for key, value in weights.items():
        if key == "legal_mandate":
            continue
        factor = 1.0 + rng.uniform(-tolerance, tolerance)
        out[key] = max(0.0, value * factor)
    total = sum(out.values()) or 1.0
    return {key: value / total for key, value in out.items()}


def run_rank_stability(requirements: list[dict], weights: dict[str, float], scorer, config: MonteCarloConfig | None = None) -> list[dict]:
    cfg = config or MonteCarloConfig()
    rng = random.Random(cfg.seed)
    observed: dict[str, list[int]] = {row["id"]: [] for row in requirements}

    for _ in range(cfg.iterations):
        trial_weights = perturb_weights(weights, rng, cfg.weight_tolerance)
        scored = []
        for row in requirements:
            scored.append((row["id"], scorer(row, trial_weights)))
        scored.sort(key=lambda item: item[1], reverse=True)
        for rank, (requirement_id, _) in enumerate(scored, start=1):
            observed[requirement_id].append(rank)

    result = []
    for requirement_id, ranks in observed.items():
        result.append({
            "id": requirement_id,
            "mean_rank": mean(ranks),
            "best_rank": min(ranks),
            "worst_rank": max(ranks),
            "stability": ranks.count(round(mean(ranks))) / len(ranks),
        })
    return sorted(result, key=lambda row: row["mean_rank"])
