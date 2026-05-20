# Render Governance Test Suite (A6)

## Determinism
- Re-render same input twice, compare normalized output checksums.

## Layout
- Verify `LAYOUT_CONTRACTS.yaml` thresholds are enforced.
- Verify overflow policy (`scale_then_paginate`) behavior.

## Contrast
- Validate all semantic token fg/bg pairs against WCAG AA (>= 4.5).

## Lineage
- Ensure lineage artifacts include required schema keys.

## Linting
- Run `RENDER_LINTER.py` and fail CI on any violation.
