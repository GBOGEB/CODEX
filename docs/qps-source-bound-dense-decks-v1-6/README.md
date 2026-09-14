# QPS Visual Knowledge System v1.6 — Source-Bound Dense Utilities + Controls

## Execution state

`SOURCE_DOV_COMPLETE_LOOP_EVIDENCE_BOUND_CONTROLS_PARTIAL`

This package executes the successor frontier frozen by merged PR #687. It does not add another architecture layer. It exercises the existing HTML/YAML/graph architecture against real QPS source decks and dense engineering content.

## Current authority

`ENGINEERING_CURATION_NOT_DESIGN_APPROVAL`

Global/project DoV remains **WITHHELD**.

The visual knowledge system provides source identity, curation, traceability and review evidence. It does not convert a visual/content PASS into design, safety, functional-safety, acceptance or release authority.

## Source-proof and DoV state

Closed:

- `V16-BD-001` — exact source PPTX bytes bound to controlled Library file/version IDs and SHA256.
- `V16-BD-002` — stable PNG render plus SHA256 for every v1.6-bound source slide.
- `EXTRACTED-TEXT-BINDING` — native PPTX text extracted for all 63 bound slides and bound by per-slide SHA256 in a controlled Library text bundle.
- `V16-BD-003` — all 63 bound source slides compared with curated engineering objects/reference targets; every slide has an explicit `KEEP`, `MERGE`, `REFERENCE` or `SUPERSEDE` disposition and `silent_drop_count = 0`.
- `V16-BD-004` — PCW scope reconciliation: `1199 kW = WCS HP`, `~1200 kW = rounded HP/HCC working representation`, `1256 kW = 1199 + 57 PVPS`, `1300 kW = 1256 + 44 QRB`.

Still open:

- `V16-BD-006` — Controls classification remains partial where discipline evidence conflicts or cause/effect is missing.
- `V16-BD-005` — LOOP source values are now scenario-bound, but transient/load validation, thermal inventory and recovery-capacity proof are still missing.
- `V16-BD-008` — graph refresh follows corrected v1.6 lineage and P0 engineering disposition.

## Evidence

- `source_lineage.yaml` — exact deck/slide-to-curated mapping with verified source digests and corrected slide bindings.
- `source_render_manifest.yaml` — all 63 bound source-slide render SHA256 values.
- `source_text_manifest.yaml` — all 63 native extracted-text SHA256 bindings and controlled text-bundle identity.
- `source_vs_curated_dov_v1_6.yaml` — slide-by-slide source-vs-curated content-trace DoV ledger.
- `source_proof_receipt.json` — bounded source-proof receipt and non-claims.
- `engineering_reconciliation_v1_6.yaml` — Utilities scope closure and partial Controls classifications.
- `loop_evidence_v1_6.yaml` — LOOP scenario/value binding with explicit missing transient predicates.

Controlled render bundle:

`/QPS/CODEX/source-proof/v1.6/QPS_v1.6_source_render_bundle_20260914.zip`

SHA256:

`f9a20d08d6c85c0bbcab58bfe57452957b5a5c1268eb30213c1fd92423a50132`

Controlled native-text bundle:

`/QPS/CODEX/source-proof/v1.6/QPS_v1.6_source_text_bundle_20260914.zip`

SHA256:

`081353101bf82a060c6a5f5fab573a11b246d0228aa251cac2696f2defb7eb52`

The source PPTX binaries remain in the controlled Library vault rather than being duplicated into Git. `source_lineage.yaml` binds each exact Library file ID + version ID + source SHA256.

## BD-003 findings

The render/text review exposed binding errors that could not be seen from filenames and nominal slide ranges alone. The corrected lineage now records, among other repairs:

- `SRC-UTIL-CORE` slide 25 is ATS/Ultimo naming material and is a `NAMING_SBS` reference, not CTRL-00/CTRL-01 content.
- `SRC-CTRL-CORE` slide 8 is cooling/HVAC architecture and references Utilities rather than serving as a Controls hierarchy source.
- `SRC-CTRL-CORE` slide 24 is support-system readiness/inhibition, not tender I/O; it binds to CTRL-06/CTRL-07.
- `SRC-CTRL-CORE` slides 22–23 are readiness/inhibition objects, not CTRL-05 interface-architecture objects.
- `SRC-NAMING-CONTROL` slides 21–24 are documentation/tagging sources and are retained as `NAMING_SBS` references rather than being counted as Controls content coverage.

This closes content-trace DoV only. Visual grammar is intentionally curated rather than pixel-reproduced; Office365/PowerPoint host-render parity remains separately unproven.

## BD-005 LOOP state

`V16-BD-005 = EVIDENCE_BOUND_OPEN_TRANSIENT_MODEL_REQUIRED`

The source evidence is now bound to one explicit working scenario: loss of off-site power with a single HCC/HP compressor on backup support. The ledger binds:

- `350 kW` electrical backup — single HP compressor basis;
- `350 kW` emergency PCW — dedicated LOOP/PAB12 basis;
- `~17 kW` residual heat — working one-HCC/350-kW-backup scenario;
- `~6 h` stabilization/recovery working window;
- `~2 h` onset concern;
- ventilation maintained for equipment safety, ODH active, and restricted occupancy wording.

The bound source slides do **not** provide the thermal inventory, transient heat balance, validated recovery capacity or physical definition of the `~2 h` onset. Therefore BD-005 cannot close and none of these values are promoted to guaranteed autonomy, safety limits or acceptance criteria.

## Non-overwrite rule

This directory is additive. Earlier v1.0b–v1.5 artefacts remain historical lineage. Promotion is by explicit review, not replacement-by-file-name.

## Immediate execution sequence

```text
source filename + slide binding
        ↓
source digest + stable source-slide render     [CLOSED: BD-001 / BD-002]
        ↓
native extracted-text binding                  [CLOSED]
        ↓
utilities scope reconciliation                  [CLOSED: BD-004]
        ↓
source-vs-curated content-trace DoV             [CLOSED: BD-003]
        ↓
controls classification                         [PARTIAL: BD-006]
        ↓
LOOP transient/load evidence                    [OPEN: BD-005]
        ↓
graph/node binding refresh                      [BD-008]
        ↓
YAML → HTML/SVG deterministic generator         [v1.7]
        ↓
bind QPS objects to #690/#691 publication       [v1.8]
```

## Definition of Done for v1.6

v1.6 is complete only when:

1. Utilities and Controls source mappings are reviewable at slide level — **DONE**.
2. no source-derived technical value is silently reconciled when sources differ — **DONE for reviewed curation; engineering OPEN/WIP remains visible**.
3. all WIP/assumption/candidate content remains visibly typed — **DONE for current v1.6 review scope**.
4. exact source SHA256 values are recorded — **DONE**.
5. stable source-slide images/renders exist for every bound source slide — **DONE**.
6. source-vs-curated review records exist for every bound slide — **DONE**.
7. graph nodes resolve to the promoted/corrected Utilities/Controls content — **OPEN: BD-008**.
8. content-loss review finds no silent material semantic loss — **DONE: explicit dispositions, silent_drop_count = 0**.
9. LOOP working values are backed by the required transient/load evidence — **OPEN: BD-005**.
10. Controls candidate signal conflicts are dispositioned by discipline evidence — **OPEN: BD-006**.

Global/project DoV remains **WITHHELD**.
