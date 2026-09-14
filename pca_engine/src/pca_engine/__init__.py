"""Generic PCA/NLPCA and empirical-control analytics public API."""

from .bradley_terry import bootstrap_bradley_terry, comparisons_from_utilities, fit_bradley_terry
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
from .decision_plotly import bt_rank_payload, scenario_delta_payload
from .dynamic_response import step_response, transfer_to_state_space
from .empirical_scenarios import compare_empirical_scenarios
from .pca_core import PCAResult, fit_pca, inverse_transform, transform
from .pca_loadings import communality, loadings, top_features
from .pca_metrics import components_for_threshold, compression_ratio, cumulative_variance
from .pca_reconstruction import reconstruction_metrics, reconstruct
from .plotly_payloads import (
    covariance_heatmap_payload,
    eigen_spectrum_payload,
    frequency_spectrum_payload,
    metric_history_payload,
    pca_loadings_payload,
    pca_scree_payload,
    reverse_pressure_payload,
    time_response_payload,
)
from .preprocessing import PreprocessResult, prepare_numeric

__all__ = [
    "PCAResult", "PreprocessResult", "fit_pca", "transform", "inverse_transform",
    "prepare_numeric", "loadings", "communality", "top_features", "cumulative_variance",
    "components_for_threshold", "compression_ratio", "reconstruct", "reconstruction_metrics",
    "matrix_diagnostics", "lu_decomposition", "confidence_interval", "sigma_crossings",
    "reverse_pressure", "convergence_diagnostics", "fourier_diagnostics", "taylor_diagnostics",
    "transfer_function_diagnostics", "closed_loop_transfer", "transfer_to_state_space", "step_response",
    "fit_bradley_terry", "bootstrap_bradley_terry", "comparisons_from_utilities",
    "compare_empirical_scenarios", "bt_rank_payload", "scenario_delta_payload",
    "metric_history_payload", "covariance_heatmap_payload", "pca_scree_payload",
    "pca_loadings_payload", "eigen_spectrum_payload", "reverse_pressure_payload",
    "frequency_spectrum_payload", "time_response_payload",
]

__version__ = "0.3.0"
