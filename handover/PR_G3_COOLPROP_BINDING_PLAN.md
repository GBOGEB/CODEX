# PR-G3 CoolProp Binding Plan

## Purpose

This PR builds on PR-G2 by starting the first executable open-source real-fluid backend path.

The target is not yet publication-grade helium validation. The target is a CI-safe CoolProp binding layer that can:

1. detect whether CoolProp is installed,
2. run real-fluid PT/PH/PS calls when available,
3. report unavailable status when absent,
4. emit state-point comparison rows compatible with the existing backend comparison report schema,
5. provide data hooks for Plotly T-s, T-h, T-g, rho-v and exergy surfaces.

---

# Why CoolProp First

CoolProp is the most practical executable backend before REFPROP and HEPAK are available.

It supports early maturation of:

- real-fluid state calls,
- saturation prototypes,
- density and specific volume surfaces,
- T-s and T-h plots,
- fallback-vs-real-fluid deltas,
- CI-friendly optional execution.

---

# Backend Tier Position

| Tier | Backend | Role |
|---|---|---|
| 0 | FallbackHeliumBackend | deterministic local baseline |
| 1 | CoolProp | open-source real-fluid candidate |
| 2 | REFPROP | canonical engineering backend |
| 3 | HEPAK | helium <5 K and two-phase specialist |
| 4 | NIST/GISTAU | reference target values |

---

# Implementation Tasks

## G3.1 CoolProp state grid builder

Create:

```text
src/gistau_ch15/properties/coolprop_state_grid.py
```

Responsibilities:

- request PT state points from CoolProp when available,
- produce fallback unavailable rows when CoolProp is absent,
- normalize outputs to JSON rows,
- prepare T/s/h/rho/v/g/exergy fields for Plotly.

## G3.2 CoolProp comparison report scaffold

Create:

```text
docs/gistau-ch15/data/coolprop_state_grid_report.json
```

Rows should include:

```text
point_id
region
T_K
P_mbar
backend
available
h_J_kg
s_J_kgK
rho_kg_m3
v_m3_kg
g_J_kg
exergy_J_kg
status
notes
```

## G3.3 HTML data hook

Create:

```text
docs/gistau-ch15/coolprop_binding_status.html
```

Purpose:

- show whether CoolProp is available,
- show target points and regions,
- link to existing low-temperature Plotly surface views,
- make missing backend state visible in GitHub Pages.

---

# Initial State Points

Use the operating regions already defined in the visual portal:

| Point | T [K] | Pressure | Region |
|---|---:|---:|---|
| P-A-SUPPLY | 4.5 | 3 bar | SHe supply |
| P-VLP-RETURN | 2-10 | 26 mbar | VLP return |
| P-DOME | 1.8-5 | 31 mbar to 2 bar | saturation/dome focus |
| P-CC-STAGE | 2-10 | 26 to 550 mbar | cold compressor |

---

# Acceptance Criteria

- CI passes without CoolProp installed.
- CoolProp absence is explicit, not silent.
- Data schema is compatible with Plotly page binding.
- No dependency is made mandatory.
- The next session can connect `GBOGEB/CoolProp` or installed CoolProp without changing public JSON schema.

---

# Deferred

- HEPAK executable calls.
- REFPROP executable calls.
- real saturation dome physics.
- He-II boundary overlays.
- final tolerance-grade reproduction.
