# PR-G Backend Binding Phase Plan

## Purpose

This phase turns the existing GISTAU Chapter 15 architecture into an executable backend-binding layer.

Previous merged work established:

- deterministic tuple calculations
- backend abstractions
- worked example fixtures
- visual/source traceability
- GitHub Pages review portal
- low-temperature Plotly surface scaffolds

PR-G focuses on backend execution readiness and numerical comparison.

---

# Phase Goal

Create a safe, optional, CI-compatible property-backend execution layer for:

1. fallback helium backend,
2. CoolProp,
3. REFPROP,
4. HEPAK,
5. NIST/GISTAU reference values.

The immediate goal is not to force all commercial/specialist libraries to run in CI. The goal is to make backend availability explicit, make unavailable backends visible, and produce structured reports that the HTML review portal can consume.

---

# Backend Tier Roles

| Tier | Backend | Role | CI behavior |
|---|---|---|---|
| 0 | FallbackHeliumBackend | deterministic offline execution | always available |
| 1 | CoolProp | open-source real-fluid candidate | optional; run if installed |
| 2 | REFPROP | canonical engineering backend | optional; unavailable status allowed |
| 3 | HEPAK | helium <5 K and two-phase specialist | optional; unavailable status allowed |
| 4 | NIST/GISTAU | reference values, not executable backend | loaded from fixtures |

---

# HEPAK Integration Goal

HEPAK is the priority backend for:

- helium below 5 K,
- near-2 K helium,
- two-phase helium,
- quality/wetness calculations,
- saturated liquid helium expansion,
- VLP return and cold-compressor checks.

The first implementation should create a clean adapter boundary and explicit unavailable-state reporting. It should not hard-fail if HEPAK is absent.

---

# CoolProp Integration Goal

CoolProp is the first open-source executable backend candidate.

Use it for:

- prototyping real-fluid property values,
- T-s and rho-v plot population,
- fallback-vs-real-fluid comparison,
- initial saturation curves where appropriate,
- local branch integration with `GBOGEB/CoolProp` in later work.

CoolProp must remain optional.

---

# REFPROP Integration Goal

REFPROP should remain the canonical engineering backend for general helium gas-region calculations and comparison against spreadsheet examples where REFPROP was used.

Use it for:

- room-temperature compressor,
- JT gas-region calculations,
- heat exchanger states,
- expander calculations outside deep two-phase regions,
- comparison to GISTAU REFPROP examples.

---

# NIST/GISTAU Reference Role

NIST/GISTAU values are not executable backends.

They provide:

- target values,
- expected outputs,
- validation deltas,
- tolerance checks,
- publication traceability.

---

# Implementation Tasks

## Task G1 — Backend selector

Create:

```text
src/gistau_ch15/properties/backend_selector.py
```

Responsibilities:

- register fallback, CoolProp, REFPROP, HEPAK, and NIST/GISTAU reference tiers,
- instantiate available optional backends safely,
- return backend availability status,
- never crash CI when optional libraries are missing.

---

## Task G2 — Adapter stubs

Create:

```text
src/gistau_ch15/properties/refprop_adapter.py
src/gistau_ch15/properties/hepak_adapter.py
```

Responsibilities:

- conform to `PropertyBackend`,
- lazy-load external libraries,
- raise `PropertyBackendUnavailable` cleanly when missing,
- define expected method surface for state and saturation calls.

---

## Task G3 — Worked example runner

Create:

```text
src/gistau_ch15/validation/worked_example_runner.py
```

Responsibilities:

- load `docs/gistau-ch15/data/worked_examples.json`,
- extract examples that can be mapped to state calls,
- produce comparison rows,
- mark unmapped rows as `mapping_pending`.

---

## Task G4 — Comparison runner

Create:

```text
src/gistau_ch15/properties/comparison_runner.py
```

Responsibilities:

- run state requests across available backends,
- compare to reference values where available,
- emit JSON report rows,
- preserve unavailable backend rows.

---

## Task G5 — Generated report placeholders

Create or update:

```text
docs/gistau-ch15/data/backend_availability.json
docs/gistau-ch15/data/backend_comparison_report.json
```

These files become the data source for:

```text
docs/gistau-ch15/backend_delta_heatmap.html
```

---

# Output Row Schema

Each row should eventually include:

```text
example_id
tuple_id
backend_name
backend_tier
reference_tier
quantity
backend_value
reference_value
absolute_delta
relative_delta
unit
status
notes
```

---

# Status Values

Use:

```text
ok
within_tolerance
outside_tolerance
backend_unavailable
reference_unavailable
mapping_pending
not_applicable
```

---

# First Worked Examples To Bind

Initial binding targets:

- WE-T00-REFPROP-H-PT-001,
- WE-T00-REFPROP-HSD-PT-002,
- WE-T02-FREE-EXPANSION-HEAT-001,
- WE-T02-SAT-LIQUID-HELIUM-003,
- WE-T04-CRYOGENIC-EXPANDER-001,
- WE-T05-CRYOGENIC-COMPRESSOR-001.

---

# Acceptance Criteria

- CI passes without CoolProp, REFPROP, or HEPAK installed.
- Fallback backend always executes.
- Optional backend unavailability is reported explicitly.
- Backend availability JSON exists.
- Backend comparison report JSON exists.
- Worked examples remain traceable by `example_id`.
- Visual portal can later consume the report without schema changes.

---

# Deferred To Later PRs

## PR-H

- real saturation dome overlays,
- phase-region maps,
- 1/T-s low-temperature plots,
- real-data Plotly overlays.

## PR-I

- full reproduction report,
- tolerance tuning,
- workbook export,
- publication-grade validation package.
