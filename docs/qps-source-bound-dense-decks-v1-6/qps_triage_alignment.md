# QPS Triage Alignment — v1.6 Source-Bound Dense Decks

## Purpose

Keep the v1.6 source-bound Utilities/Controls work aligned with the active QPS TRIAGE model without transferring authority between lanes, and bind this work to the already-merged generic publication infrastructure rather than creating another exporter.

## Parallel lanes

### Lane A — QPS Visual Knowledge System v1.6

Purpose:
- source-bind dense engineering deck content;
- preserve source slide lineage;
- expose explicit assumptions, candidates and open engineering reconciliations;
- provide graph/navigation targets for Utilities and Controls;
- prove exact source identity and per-slide render lineage before source-vs-curated promotion.

Authority:
`ENGINEERING_CURATION_NOT_DESIGN_APPROVAL`

### Lane B — QSVG QCELL visual-control lane

Purpose:
- maintain one canonical QCELL thermal MAIN;
- prove deterministic SSOT → SVG → HTML rendering;
- enforce collision/layer/thermal-semantic invariants;
- emit typed visual receipts.

Authority:
`VISUAL_SEMANTIC_ONLY`

Canonical QSVG progression includes #693 documentation reconciliation after #689 checker repair. Hosted/static HTML and pressure-overlay work remain non-blocking. Distinct-SHA repeat remains evidence-governed and cannot be inferred from one deterministic run.

### Lane C — Generic CODEX publication carrier

Merged #690/#691 provide the reusable publication plane:

`semantic SSOT → governed HTML/PPTX/PDF/Markdown/GitHub Pages → per-format hashes + native telemetry + semantic parity + cross-format parity + promotion receipt`

Authority:
`GENERIC_PUBLICATION_INFRASTRUCTURE`

QPS implication:
- `V16-BD-010` is not "invent a QPS exporter";
- it is "adapt source-bound QPS objects into the existing governed carrier and prove QPS-specific parity/content DoV";
- ODP remains separate unless implemented;
- PPTX structural/native telemetry is not Microsoft PowerPoint/Office host-reflow proof;
- generic publication success grants no QPS engineering or acceptance credit.

## Shared control philosophy

1. **SSOT before render** — render surfaces cannot silently become source authority.
2. **Exact source identity** — SHA / slide / object provenance is required for controlled promotion.
3. **Typed receipts / dispositions** — PASS must state what it proves and what it does not prove.
4. **No authority leakage** — visual quality cannot grant engineering/safety/acceptance authority.
5. **First-red execution** — repair the first concrete failing predicate before adding another architecture layer.
6. **Additive lineage** — preserve old versions and supersede explicitly.
7. **Cross-repo evidence is evidence, not automatic promotion** — a prior SHA must be joined to the exact persistent source object or independently re-hashed before full source-lineage closure.
8. **No derivative substitution** — a slide-1 census render cannot substitute for stable per-slide source renders.
9. **No duplicate-render promotion** — duplicate visual observations remain zero-credit evidence.

## v1.6 source-proof status

`source_proof_execution_v1_6.yaml` is the active BD-001/002 receipt and `source_lineage.yaml` now records persistent source locators plus typed digest/render states.

### What is bound

- all four exact source deck names resolve to persistent File Library objects;
- all required source slide ranges are bound in `source_lineage.yaml`;
- `SRC-CTRL-CORE` has a pre-existing governed W176 exact source locator + SHA256 tuple, now recorded as typed digest evidence;
- W162 contains prior source-gate SHA256 candidates for `SRC-UTIL-CORE` and `SRC-UTIL-CANONICAL-APPENDIX`.

### What is not yet bound

- independent raw-byte SHA256 repeat for all four current source objects;
- a cryptographic object-to-prior-hash join for the two Utilities objects in this pulse;
- any governed SHA256 for `SRC-NAMING-CONTROL`;
- fresh stable per-slide source renders for the bound slide population;
- per-slide render SHA256 tuples;
- slide-complete source-vs-curated dispositions.

Current typed state:
- `V16-BD-001 = PARTIAL_IDENTITY_BINDING`;
- `V16-BD-002 = BLOCKED_ON_RAW_BYTE_MATERIALIZATION`;
- `V16-BD-003 = PREDICATE_BLOCKED_BD002_FALSE`.

The current first red is:

`RAW_SOURCE_BYTE_MATERIALIZATION`

File Library references are persistent source locators but are not currently materialized as raw PPTX bytes in the executable container. No hash or render is fabricated across that boundary.

## Utilities reconciliation edge

`utilities_reconciliation_v1_6.yaml` narrows `V16-BD-004` without falsely closing it.

The source surfaces support this arithmetic decomposition candidate:

```text
1199 kW WCS HP + 57 kW PVPS = 1256 kW WCS total candidate
1256 kW + 44 kW QRB = 1300 kW facility PCW design capacity
```

This explains how `1199`, `~1200`, `~1256`, and `1300 kW` can coexist without forcing them to be the same quantity. Exact semantic labels still require the governing interface/load-basis evidence.

The same register keeps `124 kW` facility HVAC capacity distinct from `~120 kW` WCS room heat, exposes the `275 LPM` gaseous-N2 residual as unallocated rather than inventing load, and keeps PGB20 baseline/diversity role open.

## Controls classification edge

`control_signal_classification_v1_6.yaml` provides a first source-bound tender-level classification for candidate signals while keeping `V16-BD-007` L2 detail open.

Important consequences:
- MIT telemetry stays `MONITOR`/`WARNING` unless another source establishes interlock semantics;
- MIS path alone does not imply `HARD_TRIP`;
- common trip/ESD and explicit safe isolation are `HARD_TRIP` candidates because the source says so;
- HV02/HV03 remain occupancy/mode-sensitive rather than universal fast trips;
- HV06 remains non-blocking under the current working source;
- PAB12/IA can act as permissive/core-support conditions while exact timing and fail-safe logic remain detailed cause/effect work;
- QPS local autonomy on MCS loss remains a separate requirement from supervisory visibility.

## Source-vs-curated review contract

For every bound source slide that reaches rendered proof:

`SOURCE FILE + SHA → SOURCE SLIDE → SOURCE RENDER HASH → EXTRACTED CONTENT → CURATED ID → KEEP | MERGE | REFERENCE | SUPERSEDE | DROP_WITH_RATIONALE → CONTENT-LOSS VERDICT`

No slide may disappear silently. A polished curated object is not evidence that every technical statement survived.

## Active first-red topology

```text
TRACK A — SOURCE PROOF
RAW PPTX BYTE MATERIALIZATION
      ↓
V16-BD-001 independent SHA repeat / digest completion
      ↓
V16-BD-002 stable per-slide render + render hash
      ↓
V16-BD-003 source-vs-curated content-loss DoV

TRACK B — UTILITIES
V16-BD-004 semantic reconciliation confirmation
      ↓
V16-BD-005 LOOP transient/load evidence

TRACK C — CONTROLS
V16-BD-006 cause/effect/fail-safe completion
      ↓
V16-BD-007 exact L2 I/O when evidence exists

TRACK D — GRAPH
V16-BD-008 promoted v1.6 node/link refresh

TRACK E — PUBLICATION
V16-BD-010 bind QPS objects into #690/#691 carrier
```

`V16-BD-009` remains the v1.7 deterministic QPS render-hardening lane. Do not add a second publication architecture.

## Decision rule

```text
EXACT SOURCE OBJECT
   ↓
RAW BYTE MATERIALIZATION
   ↓
SHA256 + SOURCE SLIDE + STABLE RENDER + RENDER SHA256
   ↓
CURATED ENGINEERING OBJECT
   ↓
REVIEW / CLASSIFICATION
   ├── KEEP
   ├── MERGE
   ├── REFERENCE
   ├── SUPERSEDE
   └── DROP_WITH_RATIONALE
   ↓
CONTENT-LOSS VERDICT
   ↓
PROMOTED NAVIGATION / DECK SURFACE
```

No item skips a source-proof predicate merely because it already appears in a polished slide, HTML surface or prior visual census.

## Immediate next pulse

Source proof:

`RAW PPTX MATERIALIZATION → SHA256 REPEAT → PER-SLIDE RENDER/HASH → V16-BD-003`

In parallel, where independent evidence exists:

`V16-BD-004 UTILITIES CONFIRMATION + V16-BD-006 CONTROLS CAUSE/EFFECT`

Then:

`V16-BD-005 LOOP EVIDENCE → V16-BD-008 GRAPH REFRESH → V16-BD-010 PUBLICATION BINDING`

## Global boundary

`GLOBAL_PROJECT_DOV = WITHHELD`

Local source, visual, classification, reconciliation or publication proof cannot compensate for independent engineering, safety, verification, project or acceptance gates.
