# QPS Visual Knowledge System v1.6 — Source-Bound Dense Utilities + Controls

## Execution state

`SOURCE_BOUND_PARTIAL_CONTROL / FIRST_RED_NARROWED`

This package executes the successor frontier frozen by merged PR #687. It does not add another architecture layer. It exercises the existing HTML/YAML/graph architecture against real QPS source decks and dense engineering content.

## What changed from v1.5

v1.5 proved graph-to-deck/plot/table bindings and established a lineage contract, but the source side remained a placeholder.

v1.6 binds curated objects to actual recovered source deck names and exact source slide ranges:

- `QPS_Suporting_Sytems.pptx`
- `QPS_Supporting_Systems_FULL_SLINE_parallel_canonical_v3_appendix.pptx`
- `QPS_Control_Core_TOPIC - Copy.pptx`
- `QPS_naming_control_0304.pptx`

The source-control gate remains cryptographic and visual: exact source bytes/locator + verified SHA256, then stable per-slide source renders, then source-vs-curated content-loss DoV.

## Current evidence movement

Two engineering registers now narrow the P0 queue without overclaiming closure:

- `utilities_reconciliation_v1_6.yaml` — evidence-typed reconciliation of PCW/HVAC/N2/PGB20/support consequences;
- `control_signal_classification_v1_6.yaml` — tender-level signal classification with explicit L2/fail-safe/cause-effect residuals.

Cross-repo source-selection evidence in `GBOGEB/cryoplant-project` contains SHA256 records for several exact v1.6 source filenames. Those hashes are **discovered evidence**, not yet promoted into `source_lineage.yaml`, because exact byte/locator provenance still has to be bound.

## Publication architecture update

The old v1.8 wording is superseded by the merged generic CODEX publication carrier:

- #690 — receipt-governed HTML/PPTX/PDF/Markdown/GitHub Pages publication;
- #691 — deterministic PPTX/PDF publication with native structural telemetry and atomic promotion evidence.

Therefore `V16-BD-010` is now an adaptation/binding task:

`QPS source-bound semantic object → existing governed publication carrier → QPS-specific parity/content DoV`

Do **not** build a second exporter. ODP remains separate until actually implemented. OpenXML/PPTX structural telemetry does not prove Microsoft PowerPoint/Office host reflow.

## Delivered / controlled artifacts

- `source_lineage.yaml` — exact deck/slide-to-curated mapping with explicit digest state;
- `utilities_dense.md` — source-bound dense Utilities canonical candidate;
- `controls_dense.md` — source-bound dense Controls canonical candidate;
- `utilities_reconciliation_v1_6.yaml` — bounded Utilities reconciliation;
- `control_signal_classification_v1_6.yaml` — bounded Controls classification;
- `qps_triage_alignment.md` — cross-lane/cross-repo authority and execution alignment;
- `index.html` — navigable functional breakdown and deck entrypoint;
- `triage_v1_6.yaml` — first-red blockers, DoD, publication reuse and non-compensating gates.

## Non-overwrite rule

This directory is additive. Earlier v1.0b–v1.5 artefacts remain historical lineage. Promotion is by explicit review, not replacement-by-file-name.

## Authority

The material is a **source-bound engineering navigation / curation surface**. It does not silently convert working-slide statements into approved design requirements.

Where source slides contain WIP, alternatives, inconsistent totals, or unverified engineering assumptions, v1.6 preserves those states explicitly.

## Immediate execution sequence

```text
TRACK A — SOURCE PROOF
source filename + slide binding
        ↓
exact byte/locator + verified SHA256
        ↓
stable per-slide source render + render hash
        ↓
source-vs-curated KEEP/MERGE/REFERENCE/SUPERSEDE/DROP_WITH_RATIONALE
        ↓
content-loss verdict

TRACK B — UTILITIES
semantic reconciliation candidate
        ↓
governing load/interface confirmation
        ↓
LOOP transient/load evidence

TRACK C — CONTROLS
tender signal classification
        ↓
discipline cause/effect + fail-safe completion
        ↓
L2 exact I/O/marshalling when available

TRACK D — GRAPH
promoted v1.6 node/link refresh

TRACK E — PUBLICATION
adapt QPS objects to #690/#691 governed carrier
```

## Current first-red reading

- `V16-BD-001`: **PARTIAL_EVIDENCE_DISCOVERED** — hashes exist cross-repo for several exact filenames, but v1.6 byte/locator provenance binding is not closed.
- `V16-BD-002`: **OPEN** — stable slide renders and render hashes remain required.
- `V16-BD-003`: **OPEN** — comparison ledger must be slide-complete.
- `V16-BD-004`: **PARTIAL_RECONCILIATION** — arithmetic semantics narrowed; governing interface/load basis still required.
- `V16-BD-005`: **OPEN** — LOOP values remain scenario-working evidence.
- `V16-BD-006`: **PARTIAL_SUBSTANTIVE_CLASSIFICATION** — major candidate classes assigned; discipline/fail-safe residual remains.
- `V16-BD-007`: **OPEN / L2-GATED**.
- `V16-BD-008`: **OPEN**.
- `V16-BD-009`: **DEFER_TO_V1_7**.
- `V16-BD-010`: **REFRAME_BIND_EXISTING_CARRIER**.

## Definition of Done for v1.6

v1.6 is complete only when:

1. Utilities and Controls source mappings are reviewable at slide level;
2. no source-derived technical value is silently reconciled when sources differ;
3. all WIP/assumption/candidate content remains visibly typed;
4. exact source SHA256 values are bound to controlled bytes/locators;
5. stable source-slide images/renders exist for every bound source slide;
6. source-vs-curated review records exist for promoted slides;
7. each source slide has an explicit disposition;
8. graph nodes resolve to the promoted Utilities/Controls content;
9. content-loss review finds no unexplained material semantic loss;
10. open engineering uncertainty remains visible.

Until those close, state remains `SOURCE_BOUND_PARTIAL_CONTROL`.

`GLOBAL_PROJECT_DOV = WITHHELD`.
