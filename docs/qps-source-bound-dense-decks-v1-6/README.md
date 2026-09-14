# QPS Visual Knowledge System v1.6 — Current Restart Surface

**State:** `SOURCE_BOUND_PARTIAL_CONTROL`  
**First red:** `RAW_SOURCE_BYTE_MATERIALIZATION`  
**Authority:** `ENGINEERING_CURATION_NOT_DESIGN_APPROVAL`  
**Global/project DoV:** `WITHHELD`

Use these files as the restart order:

1. `triage_v1_6.yaml`
2. `source_proof_execution_v1_6.yaml`
3. `source_lineage.yaml`
4. `utilities_reconciliation_v1_6.yaml`
5. `control_signal_classification_v1_6.yaml`
6. `utilities_dense.md`
7. `controls_dense.md`
8. `qps_triage_alignment.md`
9. `index.html`

## Current source proof

All four exact source filenames resolve to persistent File Library objects. `SRC-CTRL-CORE` has a pre-existing governed W176 exact persistent-locator + SHA256 identity tuple. The two Utilities sources have persistent locators plus W162 source-gate SHA256 candidates but still need independent raw-byte re-hash binding. `SRC-NAMING-CONTROL` still lacks a governed digest in searched evidence.

No raw File Library PPTX bytes are currently materialized into the executable container. Consequently `V16-BD-002` has zero fresh per-slide render/hash tuples. Historical slide-1 census renders are not a substitute; the two Utilities slide-1 renders were duplicate observations with zero credit.

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

## Next executable chain

```text
raw PPTX materialization
  ↓
independent SHA256 repeat / missing naming digest
  ↓
stable fixed-setting render + SHA256 for every bound source slide
  ↓
BD-003 slide-complete KEEP / MERGE / REFERENCE / SUPERSEDE / DROP_WITH_RATIONALE
  ↓
content-loss verdict
```

Continue BD-004 and BD-006 in parallel only where evidence is independent. Then bind LOOP evidence, refresh graph nodes, and bind QPS semantic objects into existing #690/#691 governed publication infrastructure.

Do not build a second exporter. ODP and Microsoft Office host reflow remain separate proof boundaries. No visual/document/publication result grants unrelated engineering, safety, acceptance or project-level credit.
