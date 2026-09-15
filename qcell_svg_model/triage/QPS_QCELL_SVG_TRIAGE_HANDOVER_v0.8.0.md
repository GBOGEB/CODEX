# QPS ⇄ QCELL SVG Triage Handover v0.8.0

> **Current-state note (post #684–#689):** this file remains the historical lane-entry handover, but its original P1 execution wording is superseded by the merged canonical-MAIN, visual-control, deterministic-render and checker-repair pulses. Hosted/static HTML remains a **non-blocking expansion item** and is not a prerequisite for QSVG CONTROL.

## Purpose

Integrate the current QCELL SVG/HTML engineering handover into QPS triage without promoting visual artefacts into engineering authority.

This document is a triage/control surface only. It binds the current visual lineage, regressions, active design decisions, and next executable work into a single QPS-readable handover.

## Canonical direction

The target remains one canonical MAIN drawing with toggleable visual layers.

Canonical chain:

`SSOT YAML → versioned SVG → interactive HTML → rendered Markdown → optional PPT/PDF export`

Hosted/static publication is a downstream consumption path, not part of the core CONTROL gate. PPT is reference/export only.

## Current visual state

Historical working lineage:

- v0.7.1 — separated flow layer; smaller arrows; A/B/D/E in arrowheads; red 300 K boundary; parasitic gradients
- v0.7.2 — single canonical drawing; top manifold headers; dotted endpoint guides; items-included legend
- v0.7.3 — mixed layout and all-horizontal layout variants
- v0.7.4 — regression recovery for temperature, pressure, parasitic loads, masses
- v0.7.5 — HTML card progression with embedded SVG and plotly-like mute controls
- v0.7.6 — Draw.io four-sheet evolution review
- v0.8.0 — full engineering + coding handover package

Execution progression after this handover:

- #684 — canonical MAIN v0.7.7
- #685 — collision and layer-state control
- #686 — deterministic SSOT render and typed receipt path
- #688 — CONTROL qualification / final thermal-map repair
- #689 — post-review checker repair with live structure validation

## Draw.io visual evolution source

Latest four-sheet sequence:

1. `BSLN_0` — historical baseline; large arrows dominate and are unwanted on MAIN
2. `Copy of BSLN_0` — remove arrows/annotations and separate content into grouped regions
3. `Copy of Copy of BSLN_0` — smaller arrows moved toward legend/right side
4. `Copy of Copy of Copy of BSLN_0` — flow brought back toward body to test endpoint placement

Canonical merge interpretation:

- use Sheet 2 for grouped-region structure
- use Sheet 3 for smaller flow legend/header treatment
- use Sheet 4 for endpoint placement lessons
- preserve dotted endpoint guides
- keep large arrows optional/off by default

## Thermal model invariants

### Mass/boundary hierarchy

`300 K membrane || vacuum || 50 K shield/MLI || vacuum || 2 K interface / cold mass`

### 2 K circuit

- A supply: helium, 4.5 K, 3 bar
- B return: helium, 2–4 K, 26–31 mbar
- protected core: liquid helium / JT black-box region at 2 K

### 50 K thermal shield circuit

- D supply: 30–40 K, nominal high-pressure helium
- E return: 50–60 K, approximately +20 K across the shield
- current pressure intent: QCELL >7 bar, design constraint >10 bar, nominal around 13 barg, max around 14 barg TBD

### Parasitic loads

Outer:
- 300→50 K radiation
- 300→50 K conduction
- colour gradient: red→orange

Inner:
- 50→2 K radiation
- 50→2 K conduction
- colour gradient: orange→blue

If `T_2K_mass > T_50K_shield`, the inner parasitic path changes sign and heat can flow toward the 50 K stage.

## Colour policy

Temperature is the primary physics variable and determines the dominant colour map.

Cryogenic tags:
- 2 K
- 4 K
- 30 K
- 50 K
- 60 K
- 77 K

Warm scale:
- 77→300 K

Pressure is secondary/diagnostic and must use an independent non-thermal palette. Never reuse the temperature palette for pressure.

## Layer policy

MAIN supports governed visual-layer control for:

- thermal body / masses
- A/B/D/E flow layer
- dotted endpoint guides
- parasitic heat paths
- annotation cards where present
- temperature legend
- pressure diagnostic layer when later implemented
- teaching/debug overlays, OFF by default on canonical MAIN

Layers are for conflict testing and readability. They are not separate canonical drawings.

## P0 non-regression rules

- preserve temperature/pressure separation
- preserve one-MAIN-drawing policy
- preserve dotted endpoint logic
- prevent reintroduction of large-arrow dominance
- prevent PPT-first source-of-truth regression
- preserve exact-head deterministic render evidence
- preserve typed receipt authority=`VISUAL_SEMANTIC_ONLY`

## Current disposition

The historical `IMPROVE / VISUAL_CONTROL_BUILDOUT` state recorded by the original handover has been executed through #684–#689. The current gate is now governed by the exact-head CONTROL qualification evidence and any remaining formally open BD predicates, not by the old P1 task list.

No engineering, compliance, SAT, OPEX, negotiation, or release credit is granted by this visual lane.

## CONTROL promotion condition — reconciled

Core CONTROL requires:

- canonical MAIN accepted;
- layer-state defaults and persistence stable;
- no forbidden annotation/legend collision under the declared visual-control contract;
- temperature/pressure semantic separation stable;
- generated HTML/SVG reproducible from SSOT on exact subject SHA;
- typed visual receipt emitted and validated;
- checker predicates bound to live SVG structure rather than comments/global token presence;
- required review / local visual DoV formally closed.

The following remain **non-blocking expansion** items and do not gate CONTROL:

- GitHub Pages / externally hosted HTML path;
- pressure diagnostic overlay;
- equation-backed parasitic model;
- transient cooldown/warmup/reversal expansion.

Authority remains `VISUAL_SEMANTIC_ONLY` regardless of CONTROL state.
