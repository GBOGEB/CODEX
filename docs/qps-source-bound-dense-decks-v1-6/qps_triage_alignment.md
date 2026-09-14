# QPS Triage Alignment — v1.6 Source-Bound Dense Decks

## Purpose

Keep the v1.6 source-bound Utilities/Controls work aligned with the active QPS TRIAGE model without transferring authority between lanes, and bind this work to the already-merged generic publication infrastructure rather than creating another exporter.

## Parallel lanes

### Lane A — QPS Visual Knowledge System v1.6

Purpose:
- source-bind dense engineering deck content;
- preserve source slide lineage;
- expose explicit assumptions, candidates and open engineering reconciliations;
- provide graph/navigation targets for Utilities and Controls.

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

Canonical QSVG progression now includes #693 documentation reconciliation after #689 checker repair. Hosted/static HTML and pressure-overlay work remain non-blocking. Distinct-SHA repeat remains evidence-governed and cannot be inferred from one deterministic run.

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
7. **Cross-repo evidence is evidence, not automatic promotion** — discovered SHA/source records must still bind to exact controlled bytes/locators before v1.6 source lineage closes.

## v1.6 source-proof status

CODEX `source_lineage.yaml` still has null source digests, so `V16-BD-001` is not closed.

However, the controlled `GBOGEB/cryoplant-project` visual-selection corpus exposes SHA256 records for several exact filenames used by v1.6, including:

- `QPS_Suporting_Sytems.pptx` → `6d694db8e7ad85193f73a61a1c7b06938e3724c34401435b38a0111e656c5507`
- `QPS_Supporting_Systems_FULL_SLINE_parallel_canonical_v3_appendix.pptx` → `a629886b7af5d13e62b9b70cd10041e94dd6aa4f74234894d466843c5da87cba`
- `QPS_Control_Core_TOPIC - Copy.pptx` → `8e15b95ad2a2fefc1548367352eda0df6e2eb60eee878264c5f1f7a80579479a`

These are treated as `DISCOVERED_CROSS_REPO_EVIDENCE_NOT_YET_PROMOTED_INTO_V1_6_LINEAGE` until exact source-byte/locator provenance is bound. `QPS_naming_control_0304.pptx` still requires an equivalent exact hash evidence binding.

## Utilities reconciliation edge

`utilities_reconciliation_v1_6.yaml` now narrows `V16-BD-004` without falsely closing it.

The source surfaces support this arithmetic decomposition candidate:

```text
1199 kW WCS HP + 57 kW PVPS = 1256 kW WCS total candidate
1256 kW + 44 kW QRB = 1300 kW facility PCW design capacity
```

This explains why `1199`, `~1200`, `~1256`, and `1300 kW` can coexist without forcing them to be the same quantity. The exact semantic labels still require the governing interface/load-basis evidence.

The same register keeps `124 kW` facility HVAC capacity distinct from `~120 kW` WCS room heat, exposes the `275 LPM` gaseous-N2 residual as unallocated rather than invented load, and keeps PGB20 baseline/diversity role open.

## Controls classification edge

`control_signal_classification_v1_6.yaml` provides a first source-bound tender-level classification for the candidate signals while keeping `V16-BD-007` L2 detail open.

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
V16-BD-001 exact byte/hash/locator binding
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
SOURCE FACT
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
PROMOTED NAVIGATION / DECK SURFACE
```

No item skips the source-fact stage merely because it already appears in a polished slide or HTML view.

## Global boundary

`GLOBAL_PROJECT_DOV = WITHHELD`

Local source, visual, classification, reconciliation or publication proof cannot compensate for independent engineering, safety, verification, project or acceptance gates.
