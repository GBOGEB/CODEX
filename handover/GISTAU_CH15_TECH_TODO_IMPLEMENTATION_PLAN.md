# GISTAU Chapter 15 — Technical TODO Implementation Plan

## Purpose

This file converts the seven critical technical TODOs into phased implementation tasks, subtasks, files, tests, acceptance gates and PR sequencing.

The goal is to move from a static/reconstructive portal toward an engineering-grade cryogenic calculation framework.

---

# Implementation Philosophy

## Do not dilute the framework

Each technical TODO must:

1. attach to one or more tuple IDs,
2. create or update a named file,
3. add a validation test,
4. produce a visible proof artifact,
5. update the workbook/registers,
6. preserve fallback mode until REFPROP/HEPAK are available.

## Tuple IDs

| Tuple | Domain |
|---|---|
| T00 | Property / State Engine |
| T01 | Room-temperature Compressor |
| T02 | JT / Free Expansion |
| T03 | Heat Exchanger |
| T04 | Cryogenic Expander |
| T05 | Cryogenic Compressor / Circulator |
| T06 | Equivalent Power |

---

# Phase 0 — Stabilize Technical Scaffold

## Objective

Prepare the repository so the real thermodynamic implementation can proceed without breaking static publication.

## Tasks

### TASK-0.1 — Create canonical package layout

Create:

```text
docs/gistau-ch15/
  index.html
  styles.css
  active_v11.js
  data/
  assets/
  plots/
  downloads/
  tools/
    cryo_toolbox_v11.py
    test_cryo_toolbox_v11.py
src/gistau_ch15/
  __init__.py
  properties/
  calculations/
  validation/
  plotting/
  source/
tests/gistau_ch15/
```

Acceptance:
- static portal still opens
- Python tests still run
- no CDN dependency introduced

### TASK-0.2 — Split fallback engine into modules

Create:

```text
src/gistau_ch15/properties/base.py
src/gistau_ch15/properties/fallback_helium.py
src/gistau_ch15/calculations/compressor.py
src/gistau_ch15/calculations/jt_valve.py
src/gistau_ch15/calculations/heat_exchanger.py
src/gistau_ch15/calculations/expander.py
src/gistau_ch15/calculations/equivalent_power.py
```

Acceptance:
- all old tuple calculations still callable
- `tools/cryo_toolbox_v11.py` becomes a thin compatibility wrapper

---

# Phase 1 — TODO-01 REFPROP Adapter Integration

## Objective

Implement a clean adapter boundary for NIST REFPROP without making REFPROP mandatory.

## Affected tuples

- T00 property engine
- T01 compressor
- T02 JT valve
- T03 heat exchanger
- T04 expander
- T05 cryogenic compressor
- T06 equivalent power, optional liquefaction enthalpy

## Files to create

```text
src/gistau_ch15/properties/refprop_adapter.py
src/gistau_ch15/properties/errors.py
tests/gistau_ch15/test_refprop_adapter_contract.py
```

## Subtasks

### TASK-1.1 — Define adapter contract

Interface:

```python
class PropertyBackend:
    def state_pt(self, fluid: str, p_kpa: float, t_k: float) -> State: ...
    def state_ph(self, fluid: str, p_kpa: float, h_j_kg: float) -> State: ...
    def state_ps(self, fluid: str, p_kpa: float, s_j_kgk: float) -> State: ...
    def saturation_t(self, fluid: str, t_k: float) -> SaturationState: ...
    def saturation_p(self, fluid: str, p_kpa: float) -> SaturationState: ...
    def quality_ph(self, fluid: str, p_kpa: float, h_j_kg: float) -> float | None: ...
```

### TASK-1.2 — Implement optional REFPROP import

Requirements:
- do not fail if REFPROP is missing
- raise `PropertyBackendUnavailable`
- record REFPROP version and fluid file metadata when available

### TASK-1.3 — Add REFPROP contract tests with mocks

Test using mock backend values first.

Acceptance:
- fallback tests pass without REFPROP
- REFPROP tests skip cleanly if REFPROP missing
- API shape is stable

## Acceptance gate

```bash
python -m pytest tests/gistau_ch15/test_refprop_adapter_contract.py
```

---

# Phase 2 — TODO-02 HEPAK Adapter Integration

## Objective

Create a parallel HEPAK adapter to enable cross-checking against REFPROP.

## Files to create

```text
src/gistau_ch15/properties/hepak_adapter.py
tests/gistau_ch15/test_hepak_adapter_contract.py
```

## Subtasks

### TASK-2.1 — Define HEPAK adapter with same backend contract

Must expose identical calls as REFPROP adapter.

### TASK-2.2 — Add backend comparison utility

Create:

```text
src/gistau_ch15/properties/compare.py
```

Function:

```python
def compare_backends(backends, state_points, tolerances) -> ComparisonReport:
```

### TASK-2.3 — Add comparison report JSON

Output:

```text
docs/gistau-ch15/data/backend_comparison.json
```

Acceptance:
- fallback vs mock HEPAK comparison works
- missing HEPAK does not break static portal

---

# Phase 3 — TODO-03 Canonical Example Transcription

## Objective

Create machine-readable canonical example tables from the chapter figures.

## Files to create

```text
data/gistau_ch15/canonical_examples.csv
data/gistau_ch15/canonical_examples.schema.json
src/gistau_ch15/source/transcription.py
tests/gistau_ch15/test_canonical_examples_schema.py
```

## Canonical CSV fields

```text
example_id,tuple_id,figure,page,source_row,variable,symbol,value,unit,uncertainty,notes,status
```

## Subtasks

### TASK-3.1 — Create empty canonical example register

Populate one starter row per tuple.

### TASK-3.2 — Add schema validation

Ensure:
- tuple_id is one of T00-T06
- value is numeric when status is `captured`
- unit is non-empty
- figure/page present

### TASK-3.3 — Add transcription status dashboard

Generate:

```text
docs/gistau-ch15/data/transcription_status.json
```

Acceptance:
- portal shows captured vs pending rows
- no exact reproduction claims until row status is `validated`

---

# Phase 4 — TODO-04 True Helium Phase Boundary Near 1.8 K

## Objective

Replace placeholder phase tags with real helium phase-region detection once a real property backend is available.

## Files to create

```text
src/gistau_ch15/properties/phase.py
src/gistau_ch15/validation/phase_boundaries.py
tests/gistau_ch15/test_phase_region_contract.py
```

## Subtasks

### TASK-4.1 — Define phase region enum

```python
class PhaseRegion(Enum):
    SUBCOOLED_LIQUID = 'subcooled_liquid'
    SATURATED_LIQUID = 'saturated_liquid'
    TWO_PHASE = 'two_phase'
    SATURATED_VAPOR = 'saturated_vapor'
    SUPERHEATED_VAPOR = 'superheated_vapor'
    SUPERCRITICAL = 'supercritical'
    UNKNOWN = 'unknown'
```

### TASK-4.2 — Add phase detection using backend saturation calls

Inputs:
- P,T
- P,h
- P,s

### TASK-4.3 — Add warning masks to plots

Update:

```text
docs/gistau-ch15/data/phase_region_masks.json
```

Acceptance:
- JT valve and expander outputs include phase region
- phase region remains `UNKNOWN` under fallback model
- real backend can populate two-phase regions

---

# Phase 5 — TODO-05 Exact Vector Recreation of Figures and Tables

## Objective

Recreate canonical source figures/tables as structured data and SVG/chart outputs.

## Files to create

```text
src/gistau_ch15/source/figure_registry.py
src/gistau_ch15/source/table_registry.py
docs/gistau-ch15/data/figure_registry.json
docs/gistau-ch15/data/table_registry.json
docs/gistau-ch15/assets/recreated_figures/
```

## Subtasks

### TASK-5.1 — Figure registry

Fields:

```text
figure_id,tuple_id,page,title,caption,source_preview,recreated_svg,status
```

### TASK-5.2 — Table registry

Fields:

```text
table_id,tuple_id,page,title,source_preview,csv,status
```

### TASK-5.3 — Recreate one figure per tuple first

Initial figure targets:
- T00: property call workflow
- T01: compressor calculation chain
- T02: JT/free expansion chain
- T03: HX balance diagram
- T04: expander calculation chain
- T05: cryogenic compressor chain
- T06: equivalent power roll-up

Acceptance:
- at least seven recreated SVGs
- each linked from portal and workbook

---

# Phase 6 — TODO-06 Saturation Dome + Two-Phase Region Reconstruction

## Objective

Add real T-s/P-h/h-s saturation dome overlays once REFPROP/HEPAK is available.

## Files to create

```text
src/gistau_ch15/plotting/saturation.py
docs/gistau-ch15/data/saturation_dome.json
docs/gistau-ch15/plots/thermo_saturation.html
tests/gistau_ch15/test_saturation_data_shape.py
```

## Subtasks

### TASK-6.1 — Generate saturation data grid

Data shape:

```json
{
  "fluid": "helium",
  "backend": "REFPROP",
  "points": [
    {"T_K": 2.0, "P_kPa": 3.1, "s_liq": 0.0, "s_vap": 0.0, "h_liq": 0.0, "h_vap": 0.0}
  ]
}
```

### TASK-6.2 — Add overlays to active plots

Plots:
- T-s
- 1/T-s
- P-h
- h-s

### TASK-6.3 — Add low-temperature focus window

Focus region:
- 1.8 K to 5 K
- helium I / helium II note if source supports it

Acceptance:
- saturation overlay visible
- fallback mode clearly marks overlay unavailable

---

# Phase 7 — TODO-07 Engineering-Grade Validation Against Canonical Examples

## Objective

Create a validation report showing whether every canonical source example is reproduced within tolerance.

## Files to create

```text
src/gistau_ch15/validation/reproduce_examples.py
docs/gistau-ch15/data/reproduction_report.json
docs/gistau-ch15/reports/reproduction_report.md
tests/gistau_ch15/test_reproduction_report_schema.py
```

## Subtasks

### TASK-7.1 — Define tolerance model

Fields:

```text
variable,absolute_tolerance,relative_tolerance,unit,reason
```

### TASK-7.2 — Run reproduction

For each canonical row:
- load source value
- run calculation
- compare result
- mark pass/fail/blocked

### TASK-7.3 — Generate dashboard metrics

Metrics:
- examples_total
- examples_captured
- examples_validated
- examples_passed
- examples_failed
- examples_blocked

Acceptance:
- all examples either pass, fail with reason, or are blocked by TODO-01/02/03/04/06
- no silent unknowns

---

# PR Sequencing

## PR-A — Publish static portal scaffold

Includes:
- docs/gistau-ch15
- CI static checks
- handover docs

## PR-B — Modularize Python engine

Includes:
- src package
- tests
- compatibility wrapper

## PR-C — Property backend adapters

Includes:
- REFPROP stub/optional integration
- HEPAK stub/optional integration
- backend comparison

## PR-D — Source transcription and figure/table registers

Includes:
- canonical_examples.csv
- figure_registry.json
- table_registry.json
- recreated SVGs

## PR-E — Phase boundary and saturation dome

Includes:
- phase region logic
- saturation data
- active plot overlays

## PR-F — Reproduction validation report

Includes:
- reproduction report
- tolerance model
- validation dashboard

---

# Immediate Next Engineering Action

Start with PR-B because it enables every later technical TODO.

## PR-B checklist

```text
[ ] Create src/gistau_ch15 package
[ ] Move fallback backend to properties/fallback_helium.py
[ ] Define PropertyBackend protocol/base class
[ ] Move tuple calculations into calculations/*.py
[ ] Keep tools/cryo_toolbox_v11.py as compatibility wrapper
[ ] Add tests/gistau_ch15/test_fallback_engine.py
[ ] Add tests/gistau_ch15/test_idempotency.py
[ ] Update CI to run tests
```

## First implementation command sequence

```bash
mkdir -p src/gistau_ch15/properties
mkdir -p src/gistau_ch15/calculations
mkdir -p src/gistau_ch15/validation
mkdir -p src/gistau_ch15/plotting
mkdir -p src/gistau_ch15/source
mkdir -p tests/gistau_ch15
```

Then implement:

```text
src/gistau_ch15/properties/base.py
src/gistau_ch15/properties/fallback_helium.py
src/gistau_ch15/calculations/*.py
tests/gistau_ch15/test_fallback_engine.py
```
