"""Markdown reporting for generic PCA runs."""
from __future__ import annotations

from pathlib import Path

from .pca_core import PCAResult
from .pca_loadings import top_features
from .pca_reconstruction import reconstruction_metrics


def markdown_report(result: PCAResult) -> str:
    metrics = reconstruction_metrics(result)
    lines = [
        "# PCA Report",
        "",
        f"Rows: {result.input_matrix_.shape[0]}",
        f"Features: {result.input_matrix_.shape[1]}",
        f"Retained components: {result.n_components_}",
        f"Reconstruction RMSE: {metrics['rmse']:.6g}",
        "",
        "## Explained variance",
        "",
        "| Component | Eigenvalue | Ratio | Cumulative |",
        "|---|---:|---:|---:|",
    ]
    cumulative = 0.0
    for i, (value, ratio) in enumerate(zip(result.eigenvalues_, result.explained_variance_ratio_), start=1):
        cumulative += float(ratio)
        lines.append(f"| PC{i} | {value:.6g} | {ratio:.6f} | {cumulative:.6f} |")
    lines += ["", "## Top absolute loadings", ""]
    for i in range(result.n_components_):
        items = ", ".join(f"{name}={value:.4g}" for name, value in top_features(result, i, 5))
        lines.append(f"- PC{i+1}: {items}")
    return "\n".join(lines) + "\n"


def write_markdown_report(result: PCAResult, path: str | Path) -> Path:
    target = Path(path)
    target.write_text(markdown_report(result), encoding="utf-8")
    return target
