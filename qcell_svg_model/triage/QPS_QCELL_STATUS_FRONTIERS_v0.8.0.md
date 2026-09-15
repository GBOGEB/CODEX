# QPS × QCELL SVG — Current Status, BD, Frontiers, DoD and DoV

> **Supersession note:** the original `QSVG-P1A` execution sequence in this file is historical. It has been executed and split across merged #684 (P1A), #685 (P1B), #686 (P1C), #688 (CONTROL qualification) and #689 (post-review checker repair). Do not use the old combined P1A checklist as the current execution frontier.

## Executive state

**Lane:** QPS visual-engineering triage  
**Authority:** `VISUAL_SEMANTIC_ONLY`  
**Canonical implementation:** `qcell_svg_model/v0_7_7/`  
**Current posture:** `CONTROL_EVIDENCE_RECONCILIATION / EXPANSION_BOUNDED`

The lane has progressed beyond the original `IMPROVE_VISUAL_CONTROL_BUILDOUT` state. One canonical MAIN exists; layer-state and collision controls exist; deterministic SSOT rendering and typed receipt generation exist; and the post-#688 checker weaknesses were repaired in #689.

Hosted HTML and pressure overlays remain optional expansion work. Neither is a core CONTROL prerequisite.

---

## Executed progression

| Pulse | Outcome | State |
|---|---|---|
| #683 | governed QPS/QCELL SVG triage lane | MERGED |
| #684 | canonical MAIN v0.7.7 | MERGED |
| #685 | collision + layer-state control | MERGED |
| #686 | deterministic YAML→SVG→HTML + typed receipt path | MERGED |
| #688 | CONTROL qualification + 300 K thermal-map repair | MERGED |
| #689 | structure-aware checker repair after review | MERGED |

---

## P0 — preserve / non-regression

- [x] Single canonical MAIN policy.
- [x] Temperature remains primary colour map.
- [x] Pressure palette separated / pressure overlay deferred.
- [x] A/B/D/E semantics retained.
- [x] Dotted endpoint-guide concept retained.
- [x] PPT-first regression prohibited.
- [x] Large-arrow teaching layer OFF by default.
- [x] Visual invariants executable in fail-closed checker.
- [x] Required SVG groups validated from live parsed structure after #689.
- [x] 300 K / 50 K nominal membrane colours bound to live thermal-body structure after #689.
- [x] Deterministic exact-head render workflow exists.
- [x] Typed receipt emitter exists with producer SHA and artifact hashes.

---

## Updated BD register

| BD ID | Description | Current state | Current closure / evidence rule |
|---|---|---|---|
| QSVG-BD-001 | Canonical MAIN | IMPLEMENTED | accepted canonical v0.7.7 + governed review |
| QSVG-BD-002 | Large-arrow regression | CLOSED_IMPLEMENTATION | teaching arrows OFF by default and checker-enforced |
| QSVG-BD-003 | Annotation/text collision | CONTROLLED | fail-closed collision-box predicate; does not claim browser-font perfection |
| QSVG-BD-004 | Layer-state persistence | CONTROLLED | localStorage + governed reset-to-default |
| QSVG-BD-005 | YAML→SVG→HTML determinism | PROVEN_BY_WORKFLOW_PATH | exact-head two-render equality + tracked equality; retain CI evidence |
| QSVG-BD-006 | Pressure diagnostic overlay | OPEN_NONBLOCKING | implement later with separate non-thermal palette |
| QSVG-BD-007 | Hosted/static HTML | OPEN_NONBLOCKING | publication/consumption expansion only |
| QSVG-BD-008 | Typed visual receipt | IMPLEMENTED | generator-bound typed receipt path |
| QSVG-BD-009 | Distinct-SHA repeat | EVIDENCE_GOVERNED | retain only where distinct-SHA evidence is explicitly recorded; do not infer from one run |
| QSVG-BD-010 | CONTROL promotion | EVIDENCE_BOUND | exact-head checks + review + local visual DoV; never grants engineering authority |

These BDs bound only the visual-control lane. They do not grant or withhold engineering-design authority.

---

## Active frontiers

### F1 — CONTROL evidence reconciliation

Keep the canonical MAIN, checker, deterministic workflow and typed receipt mutually consistent after every visual change.

**Victory:** exact subject SHA passes checker + deterministic rebuild + receipt validation + required review with no authority drift.

### F2 — Federation receipt consumption

A downstream lane may consume the receipt only while preserving `VISUAL_SEMANTIC_ONLY`.

**Victory:** at least one governed consumer validates the receipt without translating visual PASS into engineering PASS.

### F3 — Optional pressure diagnostics

Add pressure only as a secondary diagnostic view with a separate non-thermal palette.

**Boundary:** non-blocking for current CONTROL.

### F4 — Hosted/static consumption

Expose committed HTML to documentation or hosted surfaces.

**Boundary:** non-blocking for current CONTROL.

### F5 — Equation/transient expansion

Equation-backed parasitic-load and transient cooldown/warmup states may be added only after preserving canonical MAIN non-regression and source authority.

---

## Current DoD

A QSVG CONTROL pulse is DONE only when the exact changed head has:

1. live-structure visual-control PASS;
2. canonical MAIN render equality against SSOT/template generation;
3. deterministic A/B render equality;
4. typed receipt generation and validation;
5. no new blocking security finding in the delta;
6. governed visual-semantic review;
7. authority remains `VISUAL_SEMANTIC_ONLY`.

Hosted HTML and pressure overlay are explicitly excluded from this core DoD.

---

## DoV

### Local / visual DoV

Requires:

- canonical MAIN accepted;
- thermal semantics stable;
- declared collision contract PASS;
- layer-state engine stable;
- deterministic YAML→SVG→HTML rebuild PASS;
- typed visual receipt PASS;
- exact-head review PASS.

Distinct-SHA repeat is additional repeatability evidence and must only be claimed when separately demonstrated.

### Federation DoV

Achieved when a downstream consumer validates the typed visual receipt while preserving `VISUAL_SEMANTIC_ONLY` authority.

### Global/project DoV

**WITHHELD.**

Visual receipts support evidence lineage and documentation; they do not independently grant engineering, SAT, OPEX, negotiation, compliance or release credit.

---

## Recommended next execution

Do **not** restart P1A/P1B/P1C.

Next work should be one of:

1. exact-head CONTROL evidence maintenance after a real visual change;
2. optional pressure diagnostic pulse;
3. hosted/static consumption pulse;
4. equation/transient expansion with source-bound physics evidence;
5. downstream receipt-consumption proof.

Any new pulse must remain first-red driven and must not reopen MAIN geometry without a concrete visual/semantic defect.
