# QPS Visual Knowledge System v1.6 — Source-Bound Dense Utilities + Controls

**State:** `SOURCE_BOUND_PARTIAL_CONTROL`  
**First red:** `RAW_SOURCE_BYTE_MATERIALIZATION`  
**Authority:** `ENGINEERING_CURATION_NOT_DESIGN_APPROVAL`  
**Global/project DoV:** `WITHHELD`

## Active controlled surfaces

- [`index.html`](index.html) — compact current navigation / first-red surface.
- [`source_lineage.yaml`](source_lineage.yaml) — exact source names, persistent File Library locators, slide bindings and typed digest/render state.
- [`source_proof_execution_v1_6.yaml`](source_proof_execution_v1_6.yaml) — BD-001/002 execution receipt (`qps-source-proof-execution/1.1`).
- [`triage_v1_6.yaml`](triage_v1_6.yaml) — authoritative current BD state and execution order.
- [`utilities_dense.md`](utilities_dense.md) + [`utilities_reconciliation_v1_6.yaml`](utilities_reconciliation_v1_6.yaml).
- [`controls_dense.md`](controls_dense.md) + [`control_signal_classification_v1_6.yaml`](control_signal_classification_v1_6.yaml).
- [`qps_triage_alignment.md`](qps_triage_alignment.md) — QPS/QSVG/#690/#691 authority boundaries.

## Source-proof movement

All four exact named source objects are located in the persistent File Library:

- `QPS_Suporting_Sytems.pptx`
- `QPS_Supporting_Systems_FULL_SLINE_parallel_canonical_v3_appendix.pptx`
- `QPS_Control_Core_TOPIC - Copy.pptx`
- `QPS_naming_control_0304.pptx`

Current evidence is deliberately typed rather than flattened:

- `SRC-CTRL-CORE` has a pre-existing governed W176 persistent-locator + SHA256 identity tuple; this pulse does not pretend an independent byte re-hash occurred.
- the two Utilities sources have persistent locators and prior W162 SHA256 candidates, but the current objects still need independent raw-byte re-hash binding.
- `SRC-NAMING-CONTROL` still lacks a governed SHA256 in the searched evidence.
- historical W176 slide-1 renders do not satisfy BD-002; the Utilities slide-1 renders were duplicate observations with zero credit.

No current tool path materialized these File Library PPTX objects as raw bytes in the executable container. Therefore no fresh per-slide render/hash evidence is claimed.

## Current BD state

```text
BD-001  PARTIAL_IDENTITY_BINDING
BD-002  BLOCKED_ON_RAW_BYTE_MATERIALIZATION
BD-003  PREDICATE_BLOCKED_BD002_FALSE
BD-004  PARTIAL_RECONCILIATION
BD-005  OPEN
BD-006  PARTIAL_SUBSTANTIVE_CLASSIFICATION
BD-007  OPEN_L2_GATED
BD-008  OPEN
BD-009  DEFER_TO_V1_7
BD-010  REFRAME_BIND_EXISTING_CARRIER
```

## Immediate execution order

```text
exact File Library object
    ↓
raw PPTX byte materialization
    ↓
independent SHA256 repeat / missing naming digest
    ↓
stable fixed-setting render + SHA256 for every bound slide
    ↓
BD-003 KEEP / MERGE / REFERENCE / SUPERSEDE / DROP_WITH_RATIONALE
    ↓
content-loss verdict
    ↓
LOOP evidence / graph refresh / #690/#691 publication binding where justified
```

## Publication boundary

Merged #690/#691 already provide the generic receipt-governed publication carrier for HTML/PPTX/PDF/Markdown/GitHub Pages. QPS binds into that carrier; it does not build another exporter.

ODP remains separate until implemented. OpenXML/PPTX structural telemetry does not prove Microsoft PowerPoint/Office host reflow.

## Non-compensating rule

No visual, navigation, documentation, classification, reconciliation or publication success grants unrelated engineering, safety, verification, acceptance or project-level credit.
