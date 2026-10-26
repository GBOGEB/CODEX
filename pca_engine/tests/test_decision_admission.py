"""Negative-path admissions for CODEX's gg_MATH consumer boundary."""
import math

from pca_engine.decision_admission import check_bt_admission


def row(a, b, win=1.0):
    return {"a": a, "b": b, "a_score": win, "b_score": 1.0 - win}


def test_strongly_connected_is_only_a_preflight():
    result = check_bt_admission(["A", "B", "C"], [
        row("A", "B"), row("B", "C"), row("C", "A")
    ])
    assert result["status"] == "BT_PREFLIGHT_ELIGIBLE"
    assert result["authority"] == "CONSUMER_PREFLIGHT_ONLY"
    assert "ranking" not in result and "strengths" not in result


def test_total_order_is_separated():
    result = check_bt_admission(["A", "B", "C"], [
        row("A", "B"), row("B", "C"), row("A", "C")
    ])
    assert result["status"] == "DEFER_NO_FINITE_MLE"
    assert not result["eligible"]


def test_disconnected_pair_populations():
    result = check_bt_admission(["A", "B", "C", "D"], [
        row("A", "B"), row("B", "A"), row("C", "D"), row("D", "C")
    ])
    assert result["status"] == "DEFER_DISCONNECTED_COMPARISON_GRAPH"


def test_ties_are_not_silently_regularized():
    result = check_bt_admission(["A", "B"], [row("A", "B", 0.5)])
    assert result["status"] == "DEFER_UNSUPPORTED_TIE"


def test_no_comparisons():
    assert check_bt_admission(["A", "B"], [])["status"] == "DEFER_NO_USABLE_COMPARISONS"


def test_invalid_unknown_id():
    assert check_bt_admission(["A", "B"], [row("X", "B")])["status"] == "DEFER_INVALID_COMPARISON"


def test_invalid_self_match():
    assert check_bt_admission(["A", "B"], [row("A", "A")])["status"] == "DEFER_INVALID_COMPARISON"


def test_invalid_duplicate_ids():
    assert check_bt_admission(["A", "A"], [])["status"] == "DEFER_INVALID_COMPARISON"


def test_invalid_nonfinite_score():
    assert check_bt_admission(["A", "B"], [row("A", "B", math.nan)])["status"] == "DEFER_INVALID_COMPARISON"


def test_invalid_boolean_score():
    assert check_bt_admission(["A", "B"], [
        {"a": "A", "b": "B", "a_score": True, "b_score": False}
    ])["status"] == "DEFER_INVALID_COMPARISON"
