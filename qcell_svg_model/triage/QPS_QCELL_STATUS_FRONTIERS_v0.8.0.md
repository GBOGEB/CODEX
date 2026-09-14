# QPS × QCELL SVG — Current Status, BD, Frontiers, DoD and DoV

## Executive state

**Lane:** QPS visual-engineering triage

**State:** `IMPROVE_VISUAL_CONTROL_BUILDOUT`

**Authority:** `VISUAL_SEMANTIC_ONLY`

**Current PR:** #683

The lane is not blocked from making useful progress. The main limitation is that the canonical MAIN rendering has not yet been consolidated and repeated at distinct SHAs. Therefore the workstream is active IMPROVE, not CONTROL.

---

## Current TODO

### P0 — preserve / non-regression

- [x] Single canonical MAIN policy declared.
- [x] Temperature remains primary colour map.
- [x] Pressure palette separated from thermal palette.
- [x] A/B/D/E semantics retained.
- [x] Dotted endpoint-guide concept retained.
- [x] PPT-first regression prohibited.
- [ ] Enforce large-arrow OFF-by-default in the actual canonical MAIN implementation.
- [ ] Convert visual invariants into executable/automated checks.

### P1 — active execution

- [ ] Build `v0.7.7 canonical MAIN`.
- [ ] Merge best visual lessons:
  - Sheet 2 → grouped-region separation;
  - Sheet 3 → smaller/right-side flow legend;
  - Sheet 4 → endpoint placement.
- [ ] Implement stable Plotly-like layer state engine.
- [ ] Add annotation/text collision scan.
- [ ] Render three states from the same source:
  - thermal-only;
  - thermal + parasitics;
  - full MAIN.
- [ ] Emit typed visual receipt / normalized QPS feature row.
- [ ] Repeat at a distinct SHA and compare normalized output.

### P2 — next controlled expansion

- [ ] Pressure diagnostic overlay.
- [ ] GitHub Pages/static hosted HTML path.
- [ ] Equation-backed parasitic model.
- [ ] Transient cooldown/warmup/reversal states.

---

## BD register

| BD ID | Description | State | Closure condition |
|---|---|---|---|
| QSVG-BD-001 | Canonical MAIN not yet consolidated | OPEN | v0.7.7 MAIN accepted from single SSOT |
| QSVG-BD-002 | Large-arrow behaviour still only policy-bounded | OPEN | large-arrow teaching layer OFF by default and tested |
| QSVG-BD-003 | Annotation/text overlap not systematically checked | OPEN | automated or deterministic collision scan PASS |
| QSVG-BD-004 | Layer state persistence not hardened | OPEN | repeated mute/unmute state behaves deterministically |
| QSVG-BD-005 | YAML→SVG→HTML determinism not runtime-proven | OPEN | two exact runs produce same normalized output |
| QSVG-BD-006 | Pressure overlay not yet integrated in canonical UI | OPEN-NONBLOCKING | separate diagnostic overlay implemented without thermal palette reuse |
| QSVG-BD-007 | Hosted HTML path not yet verified | OPEN-NONBLOCKING | GitHub Pages/static URL serves exact committed artefact |
| QSVG-BD-008 | Visual receipt schema not yet emitted | OPEN | receipt includes SHA, schema, layers, semantic checks, hashes, authority |
| QSVG-BD-009 | Distinct-SHA repeat not yet achieved | OPEN | same normalized state reproduced on N+1 SHA |
| QSVG-BD-010 | CONTROL promotion premature | WITHHELD | QSVG-G1..G9 all satisfied with repeat evidence |

These BDs do **not** imply engineering-design blockage; they bound the visual-control lane only.

---

## Frontiers

### Frontier F1 — Canonical MAIN convergence

Highest-value frontier. Collapse visual experiments into one accepted MAIN without losing the useful layer controls.

**Victory:** one source, one MAIN, multiple muted views.

### Frontier F2 — Visual receipt / federation contract

Turn the drawing into federatable evidence rather than a standalone picture.

Proposed receipt fields:
- producer repo
- exact commit SHA
- SSOT schema version
- rendered SVG SHA256
- rendered HTML SHA256
- normalized layer inventory
- thermal semantic checks
- pressure/temperature separation check
- collision-scan result
- endpoint-guide check
- authority = `VISUAL_SEMANTIC_ONLY`

### Frontier F3 — Deterministic rendering

Make regeneration boring and repeatable.

**Victory:** normalized YAML→SVG→HTML output identical across two clean executions.

### Frontier F4 — Interaction / muting control

Stabilize Plotly-like visual state controls.

**Victory:** layer state is explicit, restorable, and does not alter engineering semantics.

### Frontier F5 — Pressure diagnostics

Integrate pressure as a useful secondary analytical view without thermal-colour regression.

### Frontier F6 — Hosted consumption

Expose committed HTML as a static hosted surface consumable by QPS, Mission Control, ABACUS, and documentation lanes.

---

## DoD — Definition of Done for this PR / pulse

PR #683 is DONE when:

1. QPS triage manifest is committed.
2. Current TODO/BD/frontier register is committed.
3. Visual authority boundary is explicit.
4. QSVG-G1..G4 remain represented without regression.
5. QSVG-G5..G10 remain honestly NEXT/WITHHELD rather than fabricated PASS.
6. A concrete v0.7.7 execution pulse is selected.
7. Federation receipt structure is defined.

This PR does **not** need to solve canonical MAIN itself to meet its bounded DoD; it creates the governed lane and execution contract.

---

## DoV — Definition of Victory for the lane

### Local / visual DoV

Achieved only when:

- canonical MAIN accepted;
- temperature/pressure semantics stable;
- no major text collision;
- layer-state engine stable;
- deterministic YAML→SVG→HTML rebuild proven;
- visual receipt emitted;
- distinct-SHA repeat proven;
- hosted artefact verified.

### Federation DoV

Achieved when at least one downstream consumer accepts the typed visual receipt while preserving `VISUAL_SEMANTIC_ONLY` authority.

### Global/project DoV

**WITHHELD.**

A visual receipt may support evidence lineage and documentation, but it cannot independently grant engineering/SAT/OPEX/negotiation/release credit.

---

## Recommended next execution pulse

### QSVG-P1A — canonical MAIN merge

1. Use the current user-edited visual lineage as source steering.
2. Build v0.7.7 from one SSOT.
3. Default visible layers:
   - masses/boundaries;
   - temperature legend;
   - compact A/B/D/E headers;
   - dotted endpoints;
   - parasitics.
4. Default hidden layers:
   - big teaching arrows;
   - pressure overlay;
   - verbose annotation cards.
5. Render the three review states.
6. Emit collision report and receipt draft.
7. Commit and repeat on N+1 SHA.

This is the strongest next move because it simultaneously burns down BD-001, BD-002, BD-003, BD-004 and begins BD-005/008/009.