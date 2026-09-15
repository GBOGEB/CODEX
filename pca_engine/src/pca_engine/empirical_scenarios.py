"""Empirical scenario substitution without source-of-truth mutation."""
from __future__ import annotations

from typing import Any, Mapping, Sequence

import numpy as np


def _numeric_mapping(values: Mapping[str, float], name: str) -> dict[str, float]:
    if not values:
        raise ValueError(f"{name} must not be empty")
    result = {str(key): float(value) for key, value in values.items()}
    if not all(np.isfinite(value) for value in result.values()):
        raise ValueError(f"{name} values must be finite")
    return result


def compare_empirical_scenarios(
    baseline: Mapping[str, float],
    scenarios: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Apply tagged partial substitutions while preserving the immutable baseline.

    Each scenario is `{name: str, substitutions: {metric: value}}`. Unknown keys
    are rejected so a scenario cannot silently widen the controlled metric set.
    """
    base = _numeric_mapping(baseline, "baseline")
    rows: list[dict[str, Any]] = []
    for scenario in scenarios:
        name = str(scenario.get("name") or "")
        if not name:
            raise ValueError("each scenario requires a non-empty name")
        substitutions = _numeric_mapping(scenario.get("substitutions") or {}, f"scenario {name} substitutions")
        unknown = sorted(set(substitutions) - set(base))
        if unknown:
            raise ValueError(f"scenario {name} contains unknown metrics: {unknown}")
        values = dict(base)
        values.update(substitutions)
        delta = {key: values[key] - base[key] for key in base}
        rows.append(
            {
                "name": name,
                "evidence_class": "EMPIRICAL_SCENARIO_ONLY",
                "values": values,
                "delta_to_baseline": delta,
                "substituted_metrics": sorted(substitutions),
            }
        )
    sensitivity = {
        key: {
            "minimum": min([base[key]] + [row["values"][key] for row in rows]),
            "maximum": max([base[key]] + [row["values"][key] for row in rows]),
        }
        for key in base
    }
    for key, extrema in sensitivity.items():
        extrema["range"] = extrema["maximum"] - extrema["minimum"]
    return {
        "baseline": base,
        "scenarios": rows,
        "sensitivity": sensitivity,
        "authority": "EMPIRICAL_SCENARIO_ONLY",
        "formal_credit_delta": 0,
        "guard": "baseline/SSOT is preserved; scenarios do not create source evidence",
    }
