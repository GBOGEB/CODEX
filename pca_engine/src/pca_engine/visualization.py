"""Optional matplotlib visualizations."""
from __future__ import annotations

import numpy as np

from .pca_core import PCAResult
from .pca_loadings import loadings


def _plt():
    try:
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise RuntimeError("matplotlib is optional; install pca-engine[viz]") from exc
    return plt


def scree_plot(result: PCAResult, path: str) -> None:
    plt = _plt()
    fig, ax = plt.subplots()
    ax.plot(range(1, result.n_components_ + 1), result.explained_variance_ratio_, marker="o")
    ax.set(xlabel="Component", ylabel="Explained variance ratio", title="PCA scree plot")
    fig.tight_layout(); fig.savefig(path); plt.close(fig)


def score_plot(result: PCAResult, path: str, x_component: int = 0, y_component: int = 1) -> None:
    if result.n_components_ < 2:
        raise ValueError("score plot requires at least two components")
    plt = _plt(); fig, ax = plt.subplots()
    ax.scatter(result.scores_[:, x_component], result.scores_[:, y_component])
    ax.set(xlabel=f"PC{x_component+1}", ylabel=f"PC{y_component+1}", title="PCA scores")
    fig.tight_layout(); fig.savefig(path); plt.close(fig)


def loading_plot(result: PCAResult, path: str, component: int = 0) -> None:
    plt = _plt(); fig, ax = plt.subplots()
    vals = loadings(result)[:, component]
    ax.bar(np.arange(len(vals)), vals)
    ax.set_xticks(np.arange(len(vals)), result.feature_names_, rotation=45, ha="right")
    ax.set(ylabel="Loading", title=f"PC{component+1} loadings")
    fig.tight_layout(); fig.savefig(path); plt.close(fig)


def correlation_heatmap(result: PCAResult, path: str) -> None:
    plt = _plt(); fig, ax = plt.subplots()
    image = ax.imshow(result.correlation_matrix_, vmin=-1, vmax=1)
    ax.set_xticks(range(len(result.feature_names_)), result.feature_names_, rotation=45, ha="right")
    ax.set_yticks(range(len(result.feature_names_)), result.feature_names_)
    fig.colorbar(image, ax=ax); fig.tight_layout(); fig.savefig(path); plt.close(fig)
