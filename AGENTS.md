# Repository guidance

Preserve existing CODEX federation, mission, governance, and authority boundaries. Do not reinterpret tooling success as engineering/compliance/acceptance authority.

## Generic PCA/NLPCA lane

Work under `pca_engine/` is a reusable mathematical/statistical implementation lane.

Rules:
- keep the core domain-neutral and non-trading;
- no EMA, RSI, VWAP, market data, signals, backtesting, or broker APIs;
- no QPS engineering-authority logic in the generic package;
- keep first-principles PCA usable without sklearn;
- sklearn is validation-only and optional;
- TensorFlow/Keras is optional and NLPCA must fail gracefully when unavailable;
- tests must use synthetic/generic fixtures;
- docs must distinguish linear PCA from autoencoder NLPCA;
- deterministic numerical outputs should be reproducible at fixed inputs.

Definition of done for the PCA/NLPCA lane:
1. from `pca_engine/`, `pip install -e .` succeeds;
2. `pytest` is green;
3. the generic CSV CLI executes and writes scores/components/loadings/report outputs;
4. PCA returns scores, components, eigenvalues, explained-variance ratios and reconstruction metrics;
5. optional NLPCA reports dependency absence cleanly;
6. no trading-specific assumptions enter core modules.
