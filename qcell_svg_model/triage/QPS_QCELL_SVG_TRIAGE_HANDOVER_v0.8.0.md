# QPS ⇄ QCELL SVG Triage Handover v0.8.0

## Purpose

Integrate the current QCELL SVG/HTML engineering handover into QPS triage without promoting visual artefacts into engineering authority.

This document is a triage/control surface only. It binds the current visual lineage, regressions, active design decisions, and next executable work into a single QPS-readable handover.

## Canonical direction

The target remains one canonical MAIN drawing with toggleable visual layers.

Canonical chain:

`SSOT YAML → versioned SVG → hosted interactive HTML → rendered Markdown → optional PPT/PDF export`

PPT is reference/export only.

## Current visual state

Latest working lineage:

- v0.7.1 — separated flow layer; smaller arrows; A/B/D/E in arrowheads; red 300 K boundary; parasitic gradients
- v0.7.2 — single canonical drawing; top manifold headers; dotted endpoint guides; items-included legend
- v0.7.3 — mixed layout and all-horizontal layout variants
- v0.7.4 — regression recovery for temperature, pressure, parasitic loads, masses
- v0.7.5 — HTML card progression with embedded SVG and plotly-like mute controls
- v0.7.6 — Draw.io four-sheet evolution review
- v0.8.0 — full engineering + coding handover package

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

MAIN should support plotly-like muting for:

- thermal body / masses
- A/B/D/E flow layer
- dotted endpoint guides
- parasitic heat paths
- annotation cards
- temperature legend
- pressure diagnostic layer
- items-included legend

Layers are for conflict testing and readability. They are not separate canonical drawings.

## Known regressions / active triage

1. Large arrows repeatedly became visually dominant.
2. Flow placement drifted between iterations.
3. Annotation text can overlap coloured paths.
4. Temperature and pressure were previously conflated in one colour grammar.
5. Slide progression regressed to bare text before embedded SVG/card recovery.
6. Multiple variants risked obscuring the single-MAIN objective.

## QPS triage actions

### P0 — protect canonical semantics

- preserve temperature/pressure separation
- preserve one-MAIN-drawing policy
- preserve dotted endpoint logic
- prevent reintroduction of large-arrow dominance
- prevent PPT-first source-of-truth regression

### P1 — v0.7.7 canonical MAIN merge

Merge the strongest traits from the four Draw.io sheets:

- grouped regions from Sheet 2
- small flow legend/header from Sheet 3
- endpoint placement from Sheet 4
- Sheet 1 retained only as historical baseline

### P1 — robust layer state

- per-layer mute/unmute
- deterministic default visibility
- no geometry mutation when layers are toggled

### P1 — text-bump control

- cards sized as grouped text blocks
- avoid text-line overlap
- preserve legibility against thermal colours

### P2 — pressure diagnostic

- separate palette
- low/high pressure bands
- pressure hidden by default in temperature analysis

### P2 — SSOT generator hardening

- YAML drives labels, colours, values, visibility, lineage
- repeated generation from the same source must be idempotent

## Triage disposition

Current state: `IMPROVE / VISUAL_CONTROL_BUILDOUT`

No engineering, compliance, SAT, OPEX, negotiation, or release credit is granted by this package.

Promotion condition to CONTROL:

- canonical MAIN accepted
- layer states stable
- no major text overlap
- temperature/pressure semantics stable
- generated HTML/SVG reproducible from SSOT
- GitHub-hosted artefact path verified
