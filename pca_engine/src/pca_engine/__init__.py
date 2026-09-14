"""Generic PCA/NLPCA and empirical-control analytics public API."""

from .control_analytics import (
    closed_loop_transfer,
    confidence_interval,
    convergence_diagnostics,
    fourier_diagnostics,
    lu_decomposition,
    matrix_diagnostics,
    reverse_pressure,
    sigma_crossings,
    taylor_diagnostics,
    transfer_function_diagnostics,
)
from .dynamic_response import step_response, transfer_to_state_space
from .pca_core import PCAResult, fit_pca, inverse_transform, transform
from .pca_loadings import communality, loadings, top_features
from .pca_metrics import components_for_threshold, compression_ratio, cumulative_variance
from .pca_reconstruction import reconstruction_metrics, reconstruct
from .preprocessing import PreprocessResult, prepare_numeric

__all__ = [
    "PCAResult",
    "PreprocessResult",
    "fit_pca",
    "transform",
    "inverse_transform",
    "prepare_numeric",
    "loadings",
    "communality",
    "top_features",
    "cumulative_variance",
    "components_for_threshold",
    "compression_ratio",
    "reconstruct",
    "reconstruction_metrics",
    "matrix_diagnostics",
    "lu_decomposition",
    "confidence_interval",
    "sigma_crossings",
    "reverse_pressure",
    "convergence_diagnostics",
    "fourier_diagnostics",
    "taylor_diagnostics",
    "transfer_function_diagnostics",
    "closed_loop_transfer",
    "transfer_to_state_space",
    "step_response",
]

__version__ = "0.2.0"
