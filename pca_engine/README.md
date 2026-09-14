# Generic PCA / NLPCA Engine

Reusable, domain-neutral dimensionality-reduction package for numerical tables.

## Scope

Core PCA is implemented from first principles with NumPy covariance/eigendecomposition. `scikit-learn` is an optional validation dependency. TensorFlow/Keras is optional and used only by the NLPCA autoencoder scaffold.

Explicitly excluded: trading indicators, market data, signals, backtesting, broker APIs, and QPS authority logic.

## Install

```bash
cd pca_engine
python -m pip install -e .[dev]
```

Optional validation/visualization:

```bash
python -m pip install -e .[dev,sklearn,viz]
```

Optional NLPCA:

```bash
python -m pip install -e .[nlpca]
```

## CLI

```bash
pca-engine run input.csv --target-dir out --n-components 3
```

Outputs include `summary.json`, `scores.csv`, `components.csv`, `loadings.csv`, and `report.md`.

## Test

```bash
pytest
```

See `docs/PCA_MATH.md`, `docs/PCA_KPI_GUIDE.md`, and `docs/PCA_VS_NLPCA.md`.
