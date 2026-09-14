"""Explained-variance and compression KPIs for PCA."""
from __future__ import annotations

import numpy as np


def cumulative_variance(ratios) -> np.ndarray:
    return np.cumsum(np.asarray(ratios, dtype=float))


def components_for_threshold(ratios, threshold: float = 0.95) -> int:
    if not 0.0 < threshold <= 1.0:
        raise ValueError("threshold must satisfy 0 < threshold <= 1")
    cumulative = cumulative_variance(ratios)
    hits = np.flatnonzero(cumulative >= threshold)
    return int(hits[0] + 1) if hits.size else int(len(cumulative))


def compression_ratio(n_samples: int, n_features: int, n_components: int) -> float:
    if min(n_samples, n_features, n_components) <= 0 or n_components > n_features:
        raise ValueError("invalid dimensions")
    original = n_samples * n_features
    compressed = n_samples * n_components + n_components * n_features
    return float(original / compressed)


def condition_number(eigenvalues, *, epsilon: float = 1e-12) -> float:
    values = np.asarray(eigenvalues, dtype=float)
    positive = values[values > epsilon]
    return float("inf") if positive.size == 0 else float(positive.max() / positive.min())
