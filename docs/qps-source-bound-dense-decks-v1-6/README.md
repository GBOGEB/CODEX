# QPS Visual Knowledge System v1.6 — Source-Bound Dense Utilities + Controls

## Execution state

`IMPLEMENTATION_IN_PROGRESS / SOURCE_FILENAME_AND_SLIDE_BOUND`

This package executes the successor frontier frozen by merged PR #687. It does not add another architecture layer. It exercises the existing HTML/YAML/graph architecture against real QPS source decks and dense engineering content.

## What changed from v1.5

v1.5 proved graph-to-deck/plot/table bindings and established a lineage contract, but the source side remained a placeholder.

v1.6 now binds curated objects to actual recovered source deck names and exact source slide ranges:

- `QPS_Suporting_Sytems.pptx`
- `QPS_Supporting_Systems_FULL_SLINE_parallel_canonical_v3_appendix.pptx`
- `QPS_Control_Core_TOPIC - Copy.pptx`
- `QPS_naming_control_0304.pptx`

The next source-control gate is cryptographic: source-file SHA256 and stable per-slide source renders must be added before claiming full source-lineage CONTROL.

## Delivered in this pulse

- `source_lineage.yaml` — exact deck/slide-to-curated mapping with explicit digest state;
- `utilities_dense.md` — source-bound dense Utilities canonical candidate;
- `controls_dense.md` — source-bound dense Controls canonical candidate;
- `qps_triage_alignment.md` — relationship to the QSVG triage/control lane and authority boundaries;
- `index.html` — navigable functional breakdown and deck entrypoint;
- `triage_v1_6.yaml` — DoD, open blockers and next executable predicates.

## Non-overwrite rule

This directory is additive. Earlier v1.0b–v1.5 artefacts remain historical lineage. Promotion is by explicit review, not replacement-by-file-name.

## Authority

The material is a **source-bound engineering navigation / curation surface**. It does not silently convert working-slide statements into approved design requirements.

Where source slides contain WIP, alternatives, inconsistent totals, or unverified engineering assumptions, v1.6 preserves those states explicitly.

## Immediate execution sequence

```text
source filename + slide binding
        ↓
dense Utilities + Controls curation
        ↓
source digest + stable source-slide render
        ↓
source-vs-curated visual DoV
        ↓
graph/node binding refresh
        ↓
YAML → HTML/SVG deterministic generator
        ↓
PDF/PPTX/ODP governed export
```

## Definition of Done for v1.6

v1.6 is complete only when:

1. Utilities and Controls source mappings are reviewable at slide level;
2. no source-derived technical value is silently reconciled when sources differ;
3. all WIP/assumption/candidate content remains visibly typed;
4. exact source SHA256 values are recorded;
5. stable source-slide images/renders exist for comparison;
6. source-vs-curated review records exist for promoted slides;
7. graph nodes resolve to the promoted Utilities/Controls content;
8. content-loss review finds no material semantic loss.

Until items 4–8 close, state remains `SOURCE_BOUND_PARTIAL_CONTROL`.
