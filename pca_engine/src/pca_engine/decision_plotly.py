"""Plotly-ready payloads for Bradley-Terry and empirical scenario views."""
from __future__ import annotations

from typing import Any, Mapping, Sequence


def bt_rank_payload(fit: Mapping[str, Any], uncertainty: Mapping[str, Any] | None = None) -> dict[str, Any]:
    ranking = list(fit["ranking"])
    strengths = [float(fit["strengths"][name]) for name in ranking]
    trace: dict[str, Any] = {"type": "bar", "x": ranking, "y": strengths, "name": "BT strength"}
    if uncertainty is not None:
        items = uncertainty["items"]
        trace["error_y"] = {
            "type": "data",
            "symmetric": False,
            "array": [float(items[name]["strength_upper"]) - float(fit["strengths"][name]) for name in ranking],
            "arrayminus": [float(fit["strengths"][name]) - float(items[name]["strength_lower"]) for name in ranking],
        }
    return {
        "data": [trace],
        "layout": {"title": "Bradley-Terry action ranking", "xaxis": {"title": "Candidate"}, "yaxis": {"title": "Pairwise strength"}},
        "authority": "PAIRWISE_DECISION_ANALYTICS_ONLY",
    }


def scenario_delta_payload(scenario_result: Mapping[str, Any], *, metric: str) -> dict[str, Any]:
    baseline = scenario_result["baseline"]
    if metric not in baseline:
        raise ValueError(f"unknown metric: {metric}")
    names = ["baseline"] + [str(row["name"]) for row in scenario_result["scenarios"]]
    values = [float(baseline[metric])] + [float(row["values"][metric]) for row in scenario_result["scenarios"]]
    return {
        "data": [{"type": "bar", "x": names, "y": values, "name": metric}],
        "layout": {"title": f"Empirical scenario comparison: {metric}", "xaxis": {"title": "Scenario"}, "yaxis": {"title": metric}},
        "authority": "EMPIRICAL_SCENARIO_ONLY",
        "formal_credit_delta": 0,
    }
