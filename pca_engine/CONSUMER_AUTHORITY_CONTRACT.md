# Math consumer authority contract — CODEX

Status: proposed; never a mathematical authority transfer.

The federation mathematical SSOT is **GBOGEB/gg_MATH/kernels/**. CODEX `pca_engine` is a consumer/compatibility implementation, not the mathematical SSOT. `pca_engine/CANONICAL_API.md` and older integration reports are historical API documentation, not an override of this authority binding.

## Admission rules

1. Bind each consumed math artifact to an exact gg_MATH provider SHA, source path, declared parameters and input provenance before release use.
2. Bradley-Terry decisions must inherit the provider's fail-closed semantics (`DEFER_NO_USABLE_COMPARISONS`, `DEFER_DISCONNECTED_COMPARISON_GRAPH`, `DEFER_NO_FINITE_MLE`, `DEFER_MM_NOT_CONVERGED`). Neither `EPS` floors nor an ABACUS `prior=0.1` are evidence of an unregularized finite MLE.
3. Compare ranking/probabilities only for matched admissible populations and document normalization and regularization. PCA comparison must match centering/scaling, eigenvector sign and degenerate-eigenvalue conventions; PA95 and stability remain separate controls.
4. A local parity test cannot authorize a mathematical result or override an independent engineering or release gate.
5. If the provider is absent, outdated or unverifiable, return **UNKNOWN/DEFER** rather than treating the consumer result as canonical.

## References

- [Provider](https://github.com/GBOGEB/gg_MATH/tree/main/kernels)
- [Corrected math SSOT binding](MATH_SSOT_BINDING.md)
- [ABACUS registered math plane](https://github.com/GBOGEB/ABACUS/blob/main/federation/manifest.yaml)
- [ABACUS bridge catalog](https://github.com/GBOGEB/ABACUS/blob/main/docs/BRIDGES_AND_CONNECTIONS.md)

No provider code, external branch or release is modified by this contract.
