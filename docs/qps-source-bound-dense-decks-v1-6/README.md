# QPS Visual Knowledge System v1.6 — Source-Bound Dense Utilities + Controls

## Execution state

`SOURCE_BOUND_PARTIAL_CONTROL / RAW_SOURCE_BYTE_MATERIALIZATION_FIRST_RED`

This package executes the successor frontier frozen by merged PR #687. It does not add another architecture layer. It exercises the existing source-lineage, Utilities/Controls curation, graph/navigation and governed-publication architecture against real QPS source decks.

## Source objects now bound

v1.6 binds curated objects to these exact source deck names and slide ranges:

- `QPS_Suporting_Sytems.pptx`
- `QPS_Supporting_Systems_FULL_SLINE_parallel_canonical_v3_appendix.pptx`
- `QPS_Control_Core_TOPIC - Copy.pptx`
- `QPS_naming_control_0304.pptx`

All four exact named source objects are located in the persistent File Library and recorded in `source_lineage.yaml`.

## Source-proof movement in v1.6.2

`source_proof_execution_v1_6.yaml` (schema `qps-source-proof-execution/1.1`) records the BD-001/002 execution boundary.

- `SRC-CTRL-CORE` is joined to a pre-existing governed W176 exact source identity tuple containing the same persistent source locator and SHA256. Raw bytes were not independently re-hashed again in this pulse.
- `SRC-UTIL-CORE` and `SRC-UTIL-CANONICAL-APPENDIX` each have a persistent source object plus a W162 source-gate SHA256 candidate, but those two facts are not yet joined by an independent raw-byte re-hash in this pulse.
- earlier W176 Utilities slide-1 renders are explicitly duplicate observations and cannot satisfy BD-002.
- `SRC-NAMING-CONTROL` is located but no governed SHA256 was found in the searched evidence.
- no current tool path materialized the File Library PPTX objects as raw bytes into the execution container, so fresh stable per-slide renders and per-slide hashes are not claimed.

The first-red is exact raw-source byte materialization, followed immediately by independent SHA256 repeat and fixed-setting per-slide rendering.

## Engineering movement retained

- `utilities_reconciliation_v1_6.yaml` narrows PCW/HVAC/N2/PGB20 semantics without replacing governing load/interface evidence.
- `control_signal_classification_v1_6.yaml` provides tender-level classification while preserving discipline cause/effect, fail-safe and L2 residuals.

## Publication architecture

Merged #690/#691 already provide the generic governed publication carrier. `V16-BD-010` is therefore an adaptation/binding task:

`QPS source-bound semantic object → existing governed publication carrier → QPS-specific parity/content DoV`

Do not build a second exporter. ODP remains separate until implemented. OpenXML/PPTX structural telemetry does not prove Microsoft PowerPoint/Office host reflow.

## Controlled artefacts

- `source_lineage.yaml` — persistent source locators, exact slide bindings and typed digest/render states;
- `source_proof_execution_v1_6.yaml` — BD-001/002 evidence and blocker receipt;
- `utilities_dense.md` / `utilities_reconciliation_v1_6.yaml`;
- `controls_dense.md` / `control_signal_classification_v1_6.yaml`;
- `qps_triage_alignment.md`;
- `index.html`;
- `triage_v1_6.yaml`.

## Immediate execution sequence

```text
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
        ↓
LOOP / graph / publication binding where independently justified
```

## Current first-red reading

- `V16-BD-001 = PARTIAL_IDENTITY_BINDING`
- `V16-BD-002 = BLOCKED_ON_RAW_BYTE_MATERIALIZATION`
- `V16-BD-003 = PREDICATE_BLOCKED_BD002_FALSE`
- `V16-BD-004 = PARTIAL_RECONCILIATION`
- `V16-BD-005 = OPEN`
- `V16-BD-006 = PARTIAL_SUBSTANTIVE_CLASSIFICATION`
- `V16-BD-007 = OPEN_L2_GATED`
- `V16-BD-008 = OPEN`
- `V16-BD-009 = DEFER_TO_V1_7`
- `V16-BD-010 = REFRAME_BIND_EXISTING_CARRIER`

## v1.6 DoD boundary

v1.6 is not complete until all four exact source objects have verified digest/locator binding, every bound source slide has a stable render/hash, the slide-complete disposition/content-loss ledger exists, engineering reconciliations and LOOP evidence are explicitly dispositioned, controls classification reaches its discipline gate, and graph nodes point to promoted lineage records.

No earlier deck is overwritten and no visual/document/publication success grants engineering, safety, acceptance or project-level credit.

`GLOBAL_PROJECT_DOV = WITHHELD`.
