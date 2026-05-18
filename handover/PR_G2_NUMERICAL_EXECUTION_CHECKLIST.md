# PR-G2 Numerical/Experimental Execution Checklist

## Scope and Goal
This checklist operationalizes PR-G2 from architecture scaffolding into a canonical, executable multi-backend cryogenic validation workflow focused on numerical closure and experimental reproduction.

## Execution Order (Critical Path)
1. Real REFPROP regression baselines.
2. Real HEPAK coupling.
3. GISTAU publication reproduction.
4. Experimental cryogenic correlation.
5. Uncertainty closure studies.
6. Full wetness-aware 2 K validation.

---

## 1) Real REFPROP Regression Baselines

### Modules / Files
- `src/gistau_ch15/properties/refprop_adapter.py`
- `src/gistau_ch15/properties/comparison_runner.py`
- `src/gistau_ch15/properties/compare.py`
- `src/gistau_ch15/validation/calculation_runner.py`
- `docs/gistau-ch15/data/backend_comparison_report.json`

### Tasks
- Add version-pinned REFPROP provenance export (build, fluid package, options, unit basis).
- Generate deterministic state grids in stable single-phase and saturation-adjacent regions.
- Persist immutable baseline artifacts and include per-point metadata.
- Add regression comparator enforcing property-specific tolerances by regime.

### Tests / Checks
- `tests/gistau_ch15/test_backend_contracts.py`
- `tests/gistau_ch15/test_compare.py`
- `tests/gistau_ch15/test_idempotency.py`

### Exit Criteria
- Re-runs are deterministic within declared tolerance envelopes.
- Any drift prints worst offending state and fails CI deterministically.

---

## 2) Real HEPAK Coupling

### Modules / Files
- `src/gistau_ch15/properties/hepak_adapter.py`
- `src/gistau_ch15/properties/backend_selector.py`
- `src/gistau_ch15/properties/base.py`
- `src/gistau_ch15/properties/errors.py`
- `tests/gistau_ch15/test_backend_selector.py`
- `tests/gistau_ch15/test_backend_contracts.py`

### Tasks
- Complete HEPAK adapter input/output normalization against backend contract.
- Expose runtime availability and failure semantics in selector.
- Add cross-backend path parity runs (isobaric, isenthalpic, expander-like paths).
- Capture divergence diagnostics with state context and phase tagging.

### Exit Criteria
- HEPAK backend executes through runner without schema or unit violations.
- Backend parity report auto-generates and highlights bounded divergence zones.

---

## 3) GISTAU Publication Reproduction

### Modules / Files
- `src/gistau_ch15/visualization/workbook_export_bundle.py`
- `src/gistau_ch15/visualization/trace_json_export.py`
- `src/gistau_ch15/visualization/regenerate_overlay_json.py`
- `docs/gistau-ch15/data/visual_blocks.json`
- `docs/gistau-ch15/data/visual_source_blocks.json`
- `docs/gistau-ch15/data/worked_examples.json`

### Tasks
- Encode publication assumptions/constants as explicit machine-readable manifest.
- Reproduce source figures/tables via one-command pipeline.
- Compute numerical residual metrics versus publication references.
- Emit publication-grade JSON artifact bundle for downstream review.

### Exit Criteria
- Reproduction is one-command and deterministic.
- Figure-by-figure residuals are tracked and within declared thresholds.

---

## 4) Experimental Cryogenic Correlation

### Modules / Files
- `src/gistau_ch15/calculations/expander.py`
- `src/gistau_ch15/calculations/heat_exchanger.py`
- `src/gistau_ch15/calculations/jt_valve.py`
- `src/gistau_ch15/visualization/expander_validation.py`
- `docs/gistau-ch15/data/nist_validation_points.json`

### Tasks
- Normalize experimental datasets into a canonical schema (units + provenance).
- Add QC filters and outlier policy with deterministic handling.
- Fit regime-aware correlations and export fit diagnostics.
- Run residual structure checks (bias, leverage, heteroscedasticity indicators).

### Exit Criteria
- Correlations are reproducible and stable under resampling.
- Residual analysis shows no unresolved systematic bias in target regimes.

---

## 5) Uncertainty Closure Studies

### Modules / Files
- `src/gistau_ch15/calculations/equivalent_power.py`
- `src/gistau_ch15/kernels/exergy.py`
- `src/gistau_ch15/properties/compare.py`
- `docs/gistau-ch15/data/seed_calculation_report.json`
- `outputs/json/calculation_inputs_outputs.json`

### Tasks
- Partition uncertainty by source: measurement, backend/EOS, model-form, numerical.
- Implement propagation sweeps (Monte Carlo and/or local sensitivity).
- Rank contribution weights and identify dominant closure gaps.
- Validate predictive interval coverage on held-out experimental states.

### Exit Criteria
- Interval coverage targets are met or deviation is quantitatively explained.
- Top contributors have documented mitigation backlog items.

---

## 6) Full Wetness-Aware 2 K Validation

### Modules / Files
- `src/gistau_ch15/visualization/phase_region_classifier.py`
- `src/gistau_ch15/visualization/saturation_sampling.py`
- `src/gistau_ch15/visualization/coolprop_saturation_curves.py`
- `src/gistau_ch15/visualization/thermo_overlay_generator.py`
- `tests/gistau_ch15/test_thermo_overlay_generator.py`
- `tests/gistau_ch15/test_runtime_visualization_pipeline.py`

### Tasks
- Expand near-saturation and 2 K state-space sweeps with wetness-aware labeling.
- Stress transition continuity across phase boundaries and expander outlet states.
- Quantify stability margins and nonphysical transition detection.
- Produce acceptance envelope artifact for campaign signoff.

### Exit Criteria
- No nonphysical jumps under controlled perturbation sweeps.
- Wetness-aware acceptance envelope is generated and reviewable.

---

## CI/Test Matrix (Recommended)

### Fast deterministic (per push)
- `pytest -q tests/gistau_ch15/test_backend_selector.py`
- `pytest -q tests/gistau_ch15/test_backend_contracts.py`
- `pytest -q tests/gistau_ch15/test_compare.py`
- `pytest -q tests/gistau_ch15/test_idempotency.py`

### Medium physics validation (per PR)
- `pytest -q tests/gistau_ch15/test_runtime_visualization_pipeline.py`
- `pytest -q tests/gistau_ch15/test_thermo_overlay_generator.py`
- `pytest -q tests/test_coolprop_state_grid.py`

### Heavy reproduction/closure (scheduled)
- `pytest -q tests/gistau_ch15/test_runtime_visualization_pipeline.py tests/test_exergy_kernel.py`
- regeneration + artifact diff checks in `docs/gistau-ch15/data/*.json`

---

## Artifact and Provenance Policy
- Every generated JSON artifact must include:
  - run timestamp,
  - code commit SHA,
  - backend availability snapshot,
  - unit system declaration,
  - uncertainty model version.
- Preserve reproducibility by requiring deterministic seed capture in artifact metadata.

## Suggested Sprint Mapping
- Sprint A: Targets 1–2 (reference truth + coupling parity).
- Sprint B: Target 3 (publication reproduction).
- Sprint C: Targets 4–5 (experimental correlation + uncertainty closure).
- Sprint D: Target 6 (wetness-aware 2 K final validation + signoff).
