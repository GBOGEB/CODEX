from __future__ import annotations

import json

from pca_engine.bradley_terry import bootstrap_bradley_terry, comparisons_from_utilities, fit_bradley_terry
from pca_engine.decision_plotly import bt_rank_payload, scenario_delta_payload
from pca_engine.empirical_scenarios import compare_empirical_scenarios


def test_bradley_terry_is_reproducible_and_separate_from_pca() -> None:
    utilities = {"source_recovery": 0.9, "runtime_probe": 0.7, "framework_work": 0.2}
    comparisons = comparisons_from_utilities(utilities)
    fit = fit_bradley_terry(list(utilities), comparisons)
    assert fit["ranking"] == ["source_recovery", "runtime_probe", "framework_work"]
    assert fit["pairwise_win_probability"]["source_recovery"]["runtime_probe"] > 0.5
    assert "PCA" in fit["guard"]


def test_bootstrap_rank_uncertainty_and_plotly_payload() -> None:
    comparisons = [
        {"a": "A", "b": "B", "a_score": 1.0, "b_score": 0.0},
        {"a": "A", "b": "B", "a_score": 1.0, "b_score": 0.0},
        {"a": "A", "b": "C", "a_score": 1.0, "b_score": 0.0},
        {"a": "B", "b": "C", "a_score": 1.0, "b_score": 0.0},
        {"a": "B", "b": "C", "a_score": 1.0, "b_score": 0.0},
    ]
    fit = fit_bradley_terry(["A", "B", "C"], comparisons)
    uncertainty = bootstrap_bradley_terry(["A", "B", "C"], comparisons, bootstrap_samples=250, seed=11)
    assert uncertainty["confidence_level"] == 0.95
    assert 0.0 <= uncertainty["items"]["A"]["top_rank_probability"] <= 1.0
    payload = bt_rank_payload(fit, uncertainty)
    json.dumps(payload)
    assert payload["authority"] == "PAIRWISE_DECISION_ANALYTICS_ONLY"


def test_empirical_scenarios_preserve_baseline_and_zero_credit() -> None:
    baseline = {"mtbf_h": 100000.0, "mttr_h": 13.0, "closure_pct": 77.78}
    result = compare_empirical_scenarios(
        baseline,
        [
            {"name": "higher_mtbf", "substitutions": {"mtbf_h": 120000.0}},
            {"name": "faster_repair", "substitutions": {"mttr_h": 8.0}},
        ],
    )
    assert result["baseline"] == baseline
    assert result["formal_credit_delta"] == 0
    assert result["scenarios"][0]["evidence_class"] == "EMPIRICAL_SCENARIO_ONLY"
    assert result["scenarios"][0]["delta_to_baseline"]["mtbf_h"] == 20000.0
    payload = scenario_delta_payload(result, metric="mtbf_h")
    json.dumps(payload)
    assert payload["formal_credit_delta"] == 0
