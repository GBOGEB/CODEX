# QPS Visual Knowledge System v1.6 — Source-Bound Dense Utilities + Controls

## Execution state

`SOURCE_PROOF_BOUND_ENGINEERING_RECONCILIATION_OPEN`

This package executes the successor frontier frozen by merged PR #687. It does not add another architecture layer. It exercises the existing HTML/YAML/graph architecture against real QPS source decks and dense engineering content.

## What changed from v1.5

v1.5 proved graph-to-deck/plot/table bindings and established a lineage contract, but the source side remained a placeholder.

v1.6 binds curated objects to the recovered source deck names and exact source slide ranges:

- `QPS_Suporting_Sytems.pptx`
- `QPS_Supporting_Systems_FULL_SLINE_parallel_canonical_v3_appendix.pptx`
- `QPS_Control_Core_TOPIC - Copy.pptx`
- `QPS_naming_control_0304.pptx`

The source-proof pulse now also binds each exact PPTX byte stream to its persistent ChatGPT Library file/version identity and SHA256, confirms the native slide count, renders every v1.6-bound source slide to PNG, and records a SHA256 for every bound render.

## Source-proof closure

`V16-BD-001 = CLOSED`

`V16-BD-002 = CLOSED`

Evidence:

- `source_lineage.yaml` — source file/version identities, deck SHA256 values, slide counts and curated bindings;
- `source_render_manifest.yaml` — all 63 bound source-slide render SHA256 values;
- `source_proof_receipt.json` — bounded source-proof receipt and non-claims;
- controlled render bundle: `/QPS/CODEX/source-proof/v1.6/QPS_v1.6_source_render_bundle_20260914.zip`;
- render-bundle SHA256: `f9a20d08d6c85c0bbcab58bfe57452957b5a5c1268eb30213c1fd92423a50132`.

The source PPTX binaries remain in the controlled Library vault rather than being duplicated into the Git repository. `source_lineage.yaml` binds the exact Library file ID + version ID + SHA256 for each deck.

The only renderer anomaly observed was that the 55-slide Utilities core produced 53 PNGs because slides 54–55 were not emitted. Those two slides are outside every v1.6 source binding; all 23 bound slides in that deck rendered and hashed successfully. No claim is made for unbound slides 54–55.

## Delivered in v1.6

- `source_lineage.yaml` — exact deck/slide-to-curated mapping with verified source digests;
- `source_render_manifest.yaml` — bound slide render manifest;
- `source_proof_receipt.json` — source-proof closure receipt;
- `utilities_dense.md` — source-bound dense Utilities canonical candidate;
- `controls_dense.md` — source-bound dense Controls canonical candidate;
- `qps_triage_alignment.md` — relationship to the QSVG triage/control lane and authority boundaries;
- `index.html` — navigable functional breakdown and deck entrypoint;
- `triage_v1_6.yaml` — DoD, closed source-proof blockers and next executable predicates.

## Non-overwrite rule

This directory is additive. Earlier v1.0b–v1.5 artefacts remain historical lineage. Promotion is by explicit review, not replacement-by-file-name.

## Authority

The material is a **source-bound engineering navigation / curation surface**. It does not silently convert working-slide statements into approved design requirements.

Where source slides contain WIP, alternatives, inconsistent totals, or unverified engineering assumptions, v1.6 preserves those states explicitly.

Source proof closes identity/render predicates only. It does **not** close Utilities engineering reconciliation, Controls signal classification, LOOP evidence, source-vs-curated visual DoV, design approval, safety acceptance, or project acceptance.

## Immediate execution sequence

```text
source filename + slide binding
        ↓
source digest + stable source-slide render     [CLOSED: BD-001 / BD-002]
        ↓
utilities reconciliation + signal classification
        ↓
source-vs-curated visual DoV
        ↓
LOOP evidence
        ↓
graph/node binding refresh
        ↓
YAML → HTML/SVG deterministic generator        [v1.7]
        ↓
bind QPS objects to #690/#691 publication      [v1.8]
```

## Definition of Done for v1.6

v1.6 is complete only when:

1. Utilities and Controls source mappings are reviewable at slide level;
2. no source-derived technical value is silently reconciled when sources differ;
3. all WIP/assumption/candidate content remains visibly typed;
4. exact source SHA256 values are recorded; **DONE**
5. stable source-slide images/renders exist for every bound source slide; **DONE**
6. source-vs-curated review records exist for promoted slides;
7. graph nodes resolve to the promoted Utilities/Controls content;
8. content-loss review finds no material semantic loss.

Global/project DoV remains **WITHHELD**.
