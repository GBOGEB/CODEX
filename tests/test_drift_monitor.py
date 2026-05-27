"""Unit tests for telemetry/pca/drift_monitor.py."""

import pytest

from telemetry.pca.drift_monitor import DriftSignal, compute_drift_score, evaluate_drift


def test_drift_signal_frozen() -> None:
    """DriftSignal is frozen and immutable."""
    signal = DriftSignal(score=0.1, stable=True)
    with pytest.raises(Exception):
        signal.score = 0.2  # type: ignore[misc]


def test_compute_drift_score_identical_vectors() -> None:
    """Drift score is zero when baseline and observed are identical."""
    baseline = [0.9, 0.75, 0.4]
    observed = [0.9, 0.75, 0.4]
    assert compute_drift_score(baseline, observed) == 0.0


def test_compute_drift_score_known_deviation() -> None:
    """Drift score correctly computes mean absolute deviation."""
    baseline = [0.9, 0.75, 0.4]
    observed = [0.88, 0.71, 0.5]
    # Deviations: |0.9-0.88|=0.02, |0.75-0.71|=0.04, |0.4-0.5|=0.1
    # Mean: (0.02 + 0.04 + 0.1) / 3 = 0.16 / 3 ≈ 0.0533
    expected = (0.02 + 0.04 + 0.1) / 3
    assert abs(compute_drift_score(baseline, observed) - expected) < 1e-6


def test_compute_drift_score_empty_vectors() -> None:
    """Raises ValueError when input vectors are empty."""
    with pytest.raises(ValueError, match="input vectors must not be empty"):
        compute_drift_score([], [])


def test_compute_drift_score_mismatched_length() -> None:
    """Raises ValueError when baseline and observed have different lengths."""
    with pytest.raises(ValueError, match="baseline and observed vectors must have equal length"):
        compute_drift_score([0.9, 0.75], [0.88, 0.71, 0.5])


def test_compute_drift_score_single_element() -> None:
    """Drift score works correctly with single-element vectors."""
    baseline = [0.9]
    observed = [0.7]
    assert abs(compute_drift_score(baseline, observed) - 0.2) < 1e-6


def test_evaluate_drift_stable() -> None:
    """evaluate_drift returns stable=True when score is below threshold."""
    baseline = [0.9, 0.75, 0.4]
    observed = [0.88, 0.71, 0.5]
    signal = evaluate_drift(baseline, observed, threshold=0.15)
    assert signal.stable is True
    assert signal.score > 0.0


def test_evaluate_drift_unstable() -> None:
    """evaluate_drift returns stable=False when score exceeds threshold."""
    baseline = [0.9, 0.75, 0.4]
    observed = [0.5, 0.3, 0.1]
    signal = evaluate_drift(baseline, observed, threshold=0.15)
    assert signal.stable is False
    assert signal.score > 0.15


def test_evaluate_drift_threshold_boundary() -> None:
    """evaluate_drift correctly handles threshold boundary condition."""
    baseline = [0.0, 1.0]
    observed = [0.15, 1.15]
    # Score = (0.15 + 0.15) / 2 = 0.15
    signal = evaluate_drift(baseline, observed, threshold=0.15)
    assert abs(signal.score - 0.15) < 1e-6
    assert signal.stable is True  # stable when score <= threshold


def test_evaluate_drift_default_threshold() -> None:
    """evaluate_drift uses default threshold of 0.15."""
    baseline = [0.9, 0.75, 0.4]
    observed = [0.88, 0.71, 0.5]
    signal = evaluate_drift(baseline, observed)
    # Default threshold is 0.15, score is ~0.0533, so should be stable
    assert signal.stable is True


def test_evaluate_drift_custom_threshold() -> None:
    """evaluate_drift respects custom threshold values."""
    baseline = [0.9, 0.75, 0.4]
    observed = [0.88, 0.71, 0.5]
    # Score is ~0.0533
    signal_strict = evaluate_drift(baseline, observed, threshold=0.05)
    signal_lenient = evaluate_drift(baseline, observed, threshold=0.1)
    assert signal_strict.stable is False  # score > 0.05
    assert signal_lenient.stable is True  # score <= 0.1


def test_evaluate_drift_iterables() -> None:
    """evaluate_drift works with any iterable, not just lists."""
    baseline = (0.9, 0.75, 0.4)
    observed = (0.88, 0.71, 0.5)
    signal = evaluate_drift(baseline, observed, threshold=0.15)
    assert isinstance(signal, DriftSignal)
    assert signal.stable is True


def test_evaluate_drift_empty_vectors() -> None:
    """evaluate_drift raises ValueError for empty vectors."""
    with pytest.raises(ValueError, match="input vectors must not be empty"):
        evaluate_drift([], [])


def test_evaluate_drift_mismatched_vectors() -> None:
    """evaluate_drift raises ValueError for mismatched vector lengths."""
    with pytest.raises(ValueError, match="baseline and observed vectors must have equal length"):
        evaluate_drift([0.9, 0.75], [0.88])
