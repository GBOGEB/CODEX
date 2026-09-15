"""First-principles linear PCA using covariance eigendecomposition."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from .preprocessing import prepare_numeric


@dataclass(frozen=True)
class PCAResult:
    input_matrix_: np.ndarray
    processed_matrix_: np.ndarray
    feature_names_: list[str]
    mean_: np.ndarray
    scale_: np.ndarray
    components_: np.ndarray
    eigenvalues_: np.ndarray
    explained_variance_ratio_: np.ndarray
    scores_: np.ndarray
    covariance_matrix_: np.ndarray
    correlation_matrix_: np.ndarray
    centered_: bool
    scaled_: bool

    @property
    def n_components_(self) -> int:
        return int(self.components_.shape[0])


def fit_pca(
    data: Any,
    *,
    n_components: int | None = None,
    missing: str = "mean",
    center: bool = True,
    scale: bool = True,
) -> PCAResult:
    prep = prepare_numeric(data, missing=missing, center=center, scale=scale)
    x = prep.matrix
    n_samples, n_features = x.shape
    max_components = min(n_samples, n_features)
    if n_components is None:
        n_components = max_components
    if not 1 <= n_components <= max_components:
        raise ValueError(f"n_components must be in [1,{max_components}]")

    covariance = np.atleast_2d(np.cov(x, rowvar=False, ddof=1))
    eigenvalues_all, eigenvectors_all = np.linalg.eigh(covariance)
    order = np.argsort(eigenvalues_all)[::-1]
    eigenvalues_all = np.maximum(eigenvalues_all[order], 0.0)
    eigenvectors_all = eigenvectors_all[:, order]
    total = float(eigenvalues_all.sum())
    if total <= 0.0:
        raise ValueError("PCA is undefined because total variance is zero")

    components = eigenvectors_all[:, :n_components].T
    eigenvalues = eigenvalues_all[:n_components]
    ratios = eigenvalues / total
    scores = x @ components.T
    correlation = np.nan_to_num(np.atleast_2d(np.corrcoef(prep.input_matrix, rowvar=False)), nan=0.0)

    return PCAResult(
        input_matrix_=prep.input_matrix,
        processed_matrix_=x,
        feature_names_=prep.feature_names,
        mean_=prep.mean,
        scale_=prep.scale,
        components_=components,
        eigenvalues_=eigenvalues,
        explained_variance_ratio_=ratios,
        scores_=scores,
        covariance_matrix_=covariance,
        correlation_matrix_=correlation,
        centered_=center,
        scaled_=scale,
    )


def transform(result: PCAResult, data: Any) -> np.ndarray:
    arr = np.asarray(data, dtype=float)
    if arr.ndim != 2 or arr.shape[1] != result.components_.shape[1]:
        raise ValueError("input shape does not match fitted PCA")
    x = arr - result.mean_ if result.centered_ else arr.copy()
    if result.scaled_:
        x = x / result.scale_
    return x @ result.components_.T


def inverse_transform(result: PCAResult, scores: np.ndarray) -> np.ndarray:
    scores = np.asarray(scores, dtype=float)
    if scores.ndim != 2 or scores.shape[1] > result.n_components_:
        raise ValueError("score shape does not match fitted PCA")
    components = result.components_[: scores.shape[1]]
    x = scores @ components
    if result.scaled_:
        x = x * result.scale_
    if result.centered_:
        x = x + result.mean_
    return x
