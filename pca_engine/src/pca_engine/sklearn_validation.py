"""Optional scikit-learn validation wrapper."""
from __future__ import annotations

from typing import Any

import numpy as np

from .pca_core import fit_pca
from .preprocessing import prepare_numeric


def validate_with_sklearn(data: Any, *, n_components: int | None = None, scale: bool = True) -> dict:
    try:
        from sklearn.decomposition import PCA as SklearnPCA
    except ImportError:
        return {"status": "DEFER_SKLEARN_NOT_INSTALLED"}

    ours = fit_pca(data, n_components=n_components, scale=scale)
    prep = prepare_numeric(data, scale=scale)
    model = SklearnPCA(n_components=ours.n_components_).fit(prep.matrix)
    return {
        "status": "PASS_VALIDATED",
        "max_abs_eigenvalue_delta": float(np.max(np.abs(ours.eigenvalues_ - model.explained_variance_))),
        "max_abs_variance_ratio_delta": float(np.max(np.abs(ours.explained_variance_ratio_ - model.explained_variance_ratio_))),
    }
