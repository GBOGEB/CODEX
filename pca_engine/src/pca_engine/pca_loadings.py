"""PCA loadings, communality, and feature ranking."""
from __future__ import annotations

import numpy as np

from .pca_core import PCAResult


def loadings(result: PCAResult) -> np.ndarray:
    return result.components_.T * np.sqrt(result.eigenvalues_)


def squared_loadings(result: PCAResult) -> np.ndarray:
    values = loadings(result)
    return values * values


def communality(result: PCAResult) -> np.ndarray:
    return squared_loadings(result).sum(axis=1)


def top_features(result: PCAResult, component: int = 0, top_n: int = 5) -> list[tuple[str, float]]:
    if not 0 <= component < result.n_components_:
        raise ValueError("component index out of range")
    values = loadings(result)[:, component]
    order = np.argsort(np.abs(values))[::-1][:top_n]
    return [(result.feature_names_[i], float(values[i])) for i in order]
