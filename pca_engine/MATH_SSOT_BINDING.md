# CODEX `pca_engine` — Math SSOT Binding (correction)

**Status:** Reference / governance note. Additive. No authority transfer.
**Corrects framing in:** PR #1188 (merged).

---

## Correction

PR #1188 originally proposed making the CODEX `pca_engine` the **authority** for
PCA / Bradley-Terry across the federation. That framing was wrong and is
corrected here.

`GBOGEB/gg_MATH/kernels/` already provides this capability, and more rigorously:

- **PCA** — exact cyclic-by-row Jacobi eigendecomposition
  (`matrix_core.symmetric_eigen_jacobi`) + `parallel_analysis` (PA95) +
  `bootstrap_loading_stability`.
- **Bradley-Terry** — `rank_pairs` (MM / Hunter 2004) with fail-closed DEFER
  guards (`DEFER_NO_FINITE_MLE`, `DEFER_DISCONNECTED_COMPARISON_GRAPH`, ...).
- All kernels carry `authority_transfer = False`.

## Resolution

**gg_MATH is the mathematical single source of truth.** The CODEX `pca_engine`
is a **consumer**, not an authority. It must be **deduplicated** against the
canonical kernels rather than promoted:

1. Prefer importing / vendoring `gg_MATH/kernels/` over maintaining a parallel
   implementation.
2. Where a parallel copy is unavoidable, publish a **parity record** against the
   canonical kernels (same pattern as the QPS slide-reviewer parity contract).
3. Honour the fail-closed DEFER semantics; do not silently regularize an
   ill-posed MLE into a ranking.

## Cross-references

- Federation registration of gg_MATH as the `math` plane: **GBOGEB/ABACUS PR #2474**
  (`federation/manifest.yaml`, `federation/MATH_SSOT_BINDING.md`).
- Worked parity example: `ABACUS:qps_slide_reviewer/parity/` — verified PCA parity
  to machine precision and BT convergent-case match; one semantic divergence
  (consumer `prior=0.1` masks a `DEFER_NO_FINITE_MLE` that gg_MATH raises).
