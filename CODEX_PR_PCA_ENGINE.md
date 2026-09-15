# PR: Add generic PCA / NLPCA engine buildout

## Purpose

Add a reusable, non-trading PCA/NLPCA package scaffold for mathematical, statistical, KPI, and code-oriented dimensionality reduction workflows.

This PR intentionally separates PCA core logic from trading-specific use cases.

## Branch

`feature/generic-pca-nlpca-engine`

## CODE_BUILDOUT — 23 items

1. Add root `AGENTS.md` with repository intent, working rules, PCA separation rules, and Definition of Done.
2. Add `CODEX_PR_PCA_ENGINE.md` as the Codex execution brief and PR SSOT.
3. Add `pca_engine/README.md` explaining package purpose, install, CLI usage, and scope boundary.
4. Add `pca_engine/pyproject.toml` for editable local install.
5. Add `pca_engine/requirements.txt` with minimal runtime/test dependencies.
6. Add `src/pca_engine/__init__.py` exposing the public API.
7. Add `preprocessing.py` for numeric selection, missing-value handling, centering, scaling, and feature metadata.
8. Add `pca_core.py` with first-principles PCA using covariance/eigendecomposition or SVD.
9. Add optional sklearn validation wrapper without making sklearn required for the first-principles path.
10. Add `pca_metrics.py` for explained variance, cumulative variance, component selection, compression ratio, and condition metrics.
11. Add `pca_loadings.py` for loadings, squared loadings, communality, and top-feature extraction.
12. Add `pca_reconstruction.py` for reconstruction, reconstruction error, MSE, RMSE, and retained-variance diagnostics.
13. Add `nlpca_autoencoder.py` as an optional TensorFlow/Keras scaffold with graceful import failure.
14. Add `visualization.py` for scree plots, score plots, loading plots, and correlation heatmaps.
15. Add `reporting.py` to create Markdown PCA reports.
16. Add `cli.py` with `pca-engine run input.csv --target-dir out --n-components N`.
17. Add `examples/generic_pca_example.py` using synthetic non-trading data.
18. Add `examples/generic_nlpca_example.py` that runs only if TensorFlow is installed.
19. Add unit tests for preprocessing.
20. Add unit tests for PCA core shape, orthogonality, and variance ratios.
21. Add unit tests for metrics and component selection.
22. Add unit tests for loadings and reconstruction.
23. Add docs: `PCA_MATH.md`, `PCA_KPI_GUIDE.md`, and `PCA_VS_NLPCA.md`.

## Scope boundary

Excluded from the generic engine:

- EMA
- RSI
- VWAP
- market data
- buy/sell signals
- backtesting
- broker APIs
- QPS engineering-authority logic

## Acceptance criteria

- [ ] from `pca_engine/`, `pip install -e .` works
- [ ] `pytest` passes
- [ ] CLI can run PCA on a generic CSV
- [ ] first-principles PCA returns scores, components, eigenvalues, variance ratios
- [ ] loadings and communality are calculated
- [ ] reconstruction error is reported
- [ ] NLPCA example runs when TensorFlow is installed and otherwise fails gracefully
- [ ] docs clearly distinguish PCA and NLPCA
- [ ] no trading-specific logic exists in core modules

## Federation intent

`gg_MATH` may provide mathematical reference/test vectors. CODEX provides reusable implementation/controller capability. No QPS child engineering semantics are transferred into this package.
