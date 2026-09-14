# QPS Visual Knowledge System v1.6 — Source-Bound Dense Utilities + Controls

## Execution state

`SOURCE_BOUND_PARTIAL_CONTROL / RAW_SOURCE_BYTE_MATERIALIZATION_FIRST_RED`

This package executes the successor frontier frozen by merged PR #687. It does not add another architecture layer. It exercises the existing source-lineage, Utilities/Controls curation, graph/navigation and governed-publication architecture against real QPS source decks.

## What changed from v1.5

v1.5 proved graph-to-deck/plot/table bindings and established a lineage contract, but the source side remained a placeholder.

v1.6 binds curated objects to actual recovered source deck names and exact source slide ranges:

- `QPS_Suporting_Sytems.pptx`
- `QPS_Supporting_Systems_FULL_SLINE_parallel_canonical_v3_appendix.pptx`
- `QPS_Control_Core_TOPIC - Copy.pptx`
- `QPS_naming_control_0304.pptx`

All four exact named source objects are now located in the persistent File Library and recorded in `source_lineage.yaml`.

## Source-proof movement in v1.6.2

`source_proof_execution_v1_6.yaml` (schema `qps-source-proof-execution/1.1`) records the current BD-001/002 execution boundary.

- `SRC-CTRL-CORE` is joined to a pre-existing governed W176 exact source identity tuple containing the same persistent source locator and SHA256. The raw bytes were not independently re-hashed again in this pulse.
- `SRC-UTIL-CORE` and `SRC-UTIL-CANONICAL-APPENDIX` each have a persistent source object plus a W162 source-gate SHA256 candidate, but those two facts are not yet joined by an independent raw-byte re-hash in this pulse.
- the earlier W176 Utilities slide-1 renders are explicitly duplicate observations and cannot satisfy BD-002.
- `SRC-NAMING-CONTROL` is located but no governed SHA256 was found in the searched evidence.
- no current tool path materialized the File Library PPTX objects as raw bytes into the execution container. Therefore fresh stable per-slide renders and per-slide hashes have not been fabricated or claimed.

The first-red is therefore exact raw-source byte materialization, followed immediately by independent SHA256 repeat and fixed-setting per-slide rendering.

## Current evidence movement

Two engineering registers narrow the P0 queue without overclaiming closure:

- `utilities_reconciliation_v1_6.yaml` — evidence-typed reconciliation of PCW/HVAC/N2/PGB20/support consequences;
- `control_signal_classification_v1_6.yaml` — tender-level signal classification with explicit L2/fail-safe/cause-effect residuals.

## Publication architecture update

The old v1.8 wording is superseded by the merged generic CODEX publication carrier:

- #690 — receipt-governed HTML/PPTX/PDF/Markdown/GitHub Pages publication;
- #691 — deterministic PPTX/PDF publication with native structural telemetry and atomic promotion evidence.

Therefore `V16-BD-010` is an adaptation/binding task:

`QPS source-bound semantic object → existing governed publication carrier → QPS-specific parity/content DoV`

Do **not** build a second exporter. ODP remains separate until actually implemented. OpenXML/PPTX structural telemetry does not prove Microsoft PowerPoint/Office host reflow.

## Delivered / controlled artifacts

- `source_lineage.yaml` — persistent source locators, exact deck/slide-to-curated mapping, typed digest/render states;
- `source_proof_execution_v1_6.yaml` — BD-001/002 evidence and blocker receipt;
- `utilities_dense.md` — source-bound dense Utilities canonical candidate;
- `utilities_reconciliation_v1_6.yaml` — bounded Utilities reconciliation;
- `controls_dense.md` — source-bound dense Controls canonical candidate;
- `control_signal_classification_v1_6.yaml` — bounded Controls classification;
- `qps_triage_alignment.md` — cross-lane/cross-repo authority and execution alignment;
- `index.html` — navigable functional breakdown and deck entrypoint;
- `triage_v1_6.yaml` — live first-red blockers, DoD, publication reuse and non-compensating gates.

## Non-overwrite rule

This directory is additive. Earlier v1.0b–v1.5 artefacts remain historical lineage. Promotion is by explicit review, not replacement-by-file-name.

## Authority

The material is a **source-bound engineering navigation / curation surface**. It does not silently convert working-slide statements into approved design requirements.

Where source slides contain WIP, alternatives, inconsistent totals, unverified engineering assumptions, duplicate visual observations or incomplete provenance, v1.6 preserves those states explicitly.

## Immediate execution sequence

```text
TRACK A — SOURCE PROOF
persistent source object located
        ↓
raw PPTX byte materialization                    FIRST RED
        ↓
independent source SHA256 repeat
        ↓
stable fixed-setting render of every bound slide
        ↓
per-slide render SHA256
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

- `V16-BD-001`: **PARTIAL_IDENTITY_BINDING** — one source has a pre-existing exact governed identity tuple; two Utilities sources have locator + W162 hash candidate but still need independent raw-byte re-hash; naming/control still lacks a governed digest.
- `V16-BD-002`: **BLOCKED_ON_RAW_BYTE_MATERIALIZATION** — no fresh per-slide render set exists. Historical slide-1 census renders are insufficient and the two Utilities slide-1 renders were duplicate observations.
- `V16-BD-003`: **PREDICATE_BLOCKED_BD002_FALSE** — do not start a visual/content-loss ledger without the render predicate.
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
4. all four exact source PPTX objects have independently verified SHA256 values bound to their controlled locators;
5. every bound source slide has a stable fixed-setting render and render SHA256;
6. source-vs-curated review records exist for every promoted source slide;
7. every source slide has `KEEP / MERGE / REFERENCE / SUPERSEDE / DROP_WITH_RATIONALE` disposition;
8. graph nodes resolve to promoted Utilities/Controls content and exact lineage records;
9. content-loss review finds no silent material semantic loss;
10. all unresolved engineering uncertainty remains visible.

Until these predicates close, state remains `SOURCE_BOUND_PARTIAL_CONTROL`.

`GLOBAL_PROJECT_DOV = WITHHELD`.
