"""Generic PCA/NLPCA engine public API."""

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
]

__version__ = "0.1.0"
