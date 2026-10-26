"""N+6 source-matched adversarial BT provider preflight test family."""
from __future__ import annotations

import itertools
import math

import pytest

from pca_engine.decision_admission import check_bt_admission


def pair(a, b, score=1.0):
    return {"a": a, "b": b, "a_score": score, "b_score": 1.0 - score}


@pytest.mark.parametrize("population", list(itertools.permutations(("A", "B", "C"))))
def test_cycle_invariant_to_item_order(population):
    edges = [pair("A", "B"), pair("B", "C"), pair("C", "A")]
    r = check_bt_admission(list(population), edges)
    assert r["status"] == "BT_PREFLIGHT_ELIGIBLE"
    assert r["decisive_comparisons"] == 3
    assert "rank" not in r and "strength" not in r
    assert r["authority"] == "CONSUMER_PREFLIGHT_ONLY"


@pytest.mark.parametrize("removed_edge", (0, 1, 2))
def test_edge_deletion_breaks_strong_connectivity(removed_edge):
    cycle = [pair("A", "B"), pair("B", "C"), pair("C", "A")]
    reduced = [edge for i, edge in enumerate(cycle) if i != removed_edge]
    r = check_bt_admission(("A", "B", "C"), reduced)
    assert not r["eligible"]
    assert r["status"] == "DEFER_NO_FINITE_MLE"


@pytest.mark.parametrize("cohort", (
    None,
    [],
    ["A"],
    ["A", "A"],
    ["", "B"],
    ["A", 2],
))
def test_invalid_populations_never_rank(cohort):
    r = check_bt_admission(cohort, [])
    assert r["status"] == "DEFER_INVALID_COMPARISON"
    assert not r["eligible"]


@pytest.mark.parametrize("row", (
    None,
    5,
    {},
    {"a": ["A"], "b": "B", "a_score": 1, "b_score": 0},
    {"a": "A", "b": {"unhashable": True}, "a_score": 1, "b_score": 0},
    {"a": "A", "b": "B"},
    {"a": "A", "b": "B", "a_score": 1},
    {"a": "A", "b": "B", "a_score": -1, "b_score": 2},
    {"a": "A", "b": "B", "a_score": math.inf, "b_score": -math.inf},
    {"a": "A", "b": "B", "a_score": "1", "b_score": "0"},
    {"a": "A", "b": "B", "a_score": True, "b_score": False},
    {"a": "A", "b": "B", "a_score": 0.8, "b_score": 0.5},
))
def test_bad_rows_are_deferred_not_converted_to_votes(row):
    r = check_bt_admission(["A", "B"], [row])
    assert r["status"] == "DEFER_INVALID_COMPARISON"
    assert r["eligible"] is False


@pytest.mark.parametrize("score", (0.5, 0.25, 0.75, 0.01))
def test_weighted_or_tie_score_does_not_override_provider_contract(score):
    r = check_bt_admission(["A", "B"], [pair("A", "B", score)])
    assert r["status"] == "DEFER_UNSUPPORTED_TIE"


def test_duplicates_do_not_conjure_reverse_edge():
    r = check_bt_admission(["A", "B"], [pair("A", "B")] * 200)
    assert r["status"] == "DEFER_NO_FINITE_MLE"
    assert r["decisive_comparisons"] == 200


def test_reverse_edge_is_exactly_necessary_for_two_item_case():
    r = check_bt_admission(["A", "B"], [pair("A", "B"), pair("B", "A")])
    assert r["status"] == "BT_PREFLIGHT_ELIGIBLE"
    assert r["decisive_comparisons"] == 2


def test_isolated_fourth_item_is_not_silently_excluded():
    r = check_bt_admission(["A", "B", "C", "D"], [
        pair("A", "B"), pair("B", "C"), pair("C", "A")
    ])
    assert r["status"] == "DEFER_DISCONNECTED_COMPARISON_GRAPH"


def test_undirected_connected_but_one_way_is_separation_not_disconnected():
    r = check_bt_admission(["A", "B", "C", "D"], [
        pair("A", "B"), pair("B", "A"), pair("B", "C"),
        pair("C", "D"), pair("D", "C")
    ])
    assert r["status"] == "DEFER_NO_FINITE_MLE"


def test_partial_decisive_count_remains_descriptive_before_invalid_input():
    r = check_bt_admission(["A", "B"], [
        pair("A", "B"), {"a": "UNKNOWN", "b": "A", "a_score": 1, "b_score": 0}
    ])
    assert r["status"] == "DEFER_INVALID_COMPARISON"
    assert r["decisive_comparisons"] == 1
    assert "ranking" not in r


def test_empty_comparisons_never_masquerade_as_100_percent_coverage():
    r = check_bt_admission(["A", "B"], [])
    assert r["decisive_comparisons"] == 0
    assert r["status"] == "DEFER_NO_USABLE_COMPARISONS"


def test_boolean_ids_not_coerced():
    r = check_bt_admission(["A", True], [])
    assert r["status"] == "DEFER_INVALID_COMPARISON"
