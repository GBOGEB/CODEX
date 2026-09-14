# QPS Triage Alignment — v1.6 Source-Bound Dense Decks

## Purpose

Keep the v1.6 source-bound Utilities/Controls work aligned with the active QPS TRIAGE model without transferring authority between lanes.

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

Merged progression observed in CODEX:
- #683 triage integration
- #684 canonical MAIN
- #685 visual-control automation
- #686 deterministic renderer / receipt path
- #688 CONTROL qualification attempt
- #689 post-review checker repair

The #689 repair closes the two concrete checker defects raised after #688 by replacing raw-regex structural discovery with structure-aware live-SVG validation and element-bound 300 K / 50 K predicates. That QSVG lane should not be reimplemented inside v1.6.

## Shared control philosophy

Both lanes follow the same higher-order rules:

1. **SSOT before render** — render surfaces cannot silently become source authority.
2. **Exact source identity** — SHA / slide / object provenance is required for controlled promotion.
3. **Typed receipts / dispositions** — PASS must state what it proves and what it does not prove.
4. **No authority leakage** — visual quality cannot grant engineering/safety/acceptance authority.
5. **First-red execution** — repair the first concrete failing predicate before adding another architecture layer.
6. **Additive lineage** — preserve old versions and supersede explicitly.

## v1.6 QPS TRIAGE pressure surface

### P0 — source integrity

- source-file SHA256;
- exact source slide renders;
- source-vs-curated comparison;
- no fabricated slide identities;
- no silent deletion of technical statements.

### P0 — engineering reconciliation

- cooling-load basis: 1199 / ~1200 / ~1256 kW surfaces;
- HVAC 124 kW versus ~120 kW room-heat context;
- Gaseous-N2 total versus listed subsystem allocations;
- LOOP 17 kW / 350 kW / ~6 h / ~2 h evidence chain;
- PGB20 role and diversity basis;
- HV03/HV02/HV06 mode-specific consequence.

### P0 — controls classification

- candidate I/O → signal class;
- monitor / warning / permissive / hard trip / mode inhibit / occupancy constraint;
- MIT / MIS / MCS boundary;
- MCS-loss autonomy;
- QINFRA S/U/W control authority.

### P1 — navigation / graph burn-in

After P0 source and classification work:
- refresh WCS/HCC/QINFRA/QPS:CIS node pages;
- bind exact Utilities/Controls slide IDs;
- expose lineage and open validation items from graph-node inspectors.

### P1 — render hardening

Defer to v1.7/v1.8 rather than mixing into this pulse:
- true YAML → SVG/HTML generator;
- receipt-governed PDF/PPTX/ODP publication.

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

## Immediate next pulse after this PR

If source binaries can be ingested into a controlled repository/source-vault path, execute:

`V16-P1 = SOURCE_DIGEST + SLIDE_RENDER + SOURCE_VS_CURATED`

In parallel, engineering review can execute:

`V16-P2 = UTILITIES_RECONCILIATION + CONTROL_SIGNAL_CLASSIFICATION`

These can proceed concurrently because they consume the same source-bound manifest but close different predicates.
