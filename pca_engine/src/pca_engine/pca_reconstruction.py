"""PCA reconstruction and reconstruction-error metrics."""
from __future__ import annotations

import numpy as np

from .pca_core import PCAResult


def reconstruct(result: PCAResult, *, n_components: int | None = None) -> np.ndarray:
    k = result.n_components_ if n_components is None else int(n_components)
    if not 1 <= k <= result.n_components_:
        raise ValueError("n_components out of fitted range")
    processed = result.scores_[:, :k] @ result.components_[:k]
    raw = processed * result.scale_ if result.scaled_ else processed
    if result.centered_:
        raw = raw + result.mean_
    return raw


def reconstruction_metrics(result: PCAResult, *, n_components: int | None = None) -> dict:
    k = result.n_components_ if n_components is None else int(n_components)
    rebuilt = reconstruct(result, n_components=k)
    residual = result.input_matrix_ - rebuilt
    mse = float(np.mean(residual * residual))
    return {
        "n_components": k,
        "mse": mse,
        "rmse": float(np.sqrt(mse)),
        "max_abs_error": float(np.max(np.abs(residual))),
        "retained_variance_ratio": float(np.sum(result.explained_variance_ratio_[:k])),
    }
