# QPS Triage Alignment — v1.6

## Authority lanes

- **QPS source-bound Utilities/Controls:** `ENGINEERING_CURATION_NOT_DESIGN_APPROVAL`.
- **D2.1 / D2.2:** named engineering evidence and provenance anchors; temporal age is tracked separately from source authority.
- **QSVG QCELL visual-control:** `VISUAL_SEMANTIC_ONLY`; hosted/static HTML and pressure overlay remain non-blocking.
- **Generic publication #690/#691:** `GENERIC_PUBLICATION_INFRASTRUCTURE`; reuse it rather than creating another QPS exporter. ODP and Microsoft PowerPoint/Office host reflow remain separate proof boundaries.

## Source-proof state

The authoritative retained execution evidence is now:

- `source_proof_receipt.json`: exact source bytes hashed for all four source PPTX objects;
- `source_render_manifest.yaml`: stable render/hash evidence for all 63 bound slides;
- `source_text_manifest.yaml`: native source text bound to those slide identities;
- `source_vs_curated_dov_v1_6.yaml`: 63/63 explicit source-to-curation dispositions with no silent drop;
- `state_reconciliation_v1_6.yaml`: reconciles the later stale-branch state collision without deleting useful child artifacts.

Therefore BD-001 and BD-002 are CLOSED, native-text binding is CLOSED, and BD-003 is `CLOSED_CONTENT_TRACE_DOV`. These are source/curation claims only; they do not grant engineering or acceptance authority.

## D2.1 / D2.2 source policy

The governing distinction is:

```text
SOURCE AGE / MATURITY  !=  PROVENANCE / EVIDENCE AUTHORITY
```

**D2.1 Preliminary Design — SCK CEN/81777062** remains a specific preliminary-design anchor. **D2.2 Technical Specification for MINERVA Cryogenic System — DSBT-TN-2024-19 Rev 4.0** remains a specific technical-specification anchor.

The Addendum applicable-documents section explicitly says SCK CEN supplies information at the maturity needed for the offer and may provide updated versions during Contract execution. Therefore an anchor can be temporarily aged while still remaining essential evidence and provenance.

Operational rules:

- do not delete or weaken D2.1/D2.2 merely because later sources exist;
- use later sources to create a traceable refinement/deviation/change edge;
- require current revision/change status before claiming a final current design point;
- only explicit governed revision, withdrawal or approved change may justify `SUPERSEDED` at requirement/value level;
- preserve the exact originating source even after a later design point is selected.

For BD-005 this means D2.1 remains authoritative for its Line-S/cryogenic-return evidence lane, while D2.2 supplies anchored WCS-room geometry, normal site-interface and loss-of-utility test evidence. Neither lane can be used to manufacture missing evidence in the other by analogy.

## Engineering edges

BD-004's semantic scope reconciliation remains closed for the `1199 / ~1200 / 1256 / 1300 kW` labels, while coolant sizing/facility approval and current revision/change lineage remain separate questions.

BD-005 remains OPEN. Current pressure points are:

1. current governed revision/change lineage around D2.1/D2.2 and later interfaces;
2. exact one-HP LOOP electrical/VFD operating point and ES02 auxiliary split;
3. emergency PAB12 hydraulic state;
4. HV03 degraded/LOOP airflow, ducting and heat-removal state;
5. effective room/equipment thermal mass;
6. physical definition of `~2 h` onset;
7. measurable definition of `~6 h` stabilization;
8. first-law WCS transient with uncertainty and independent review.

BD-006 remains tender-level partial. MIT/MIS/MCS path does not itself determine trip severity, and D2.2 loss-of-utility safe-shutdown test intent does not automatically create a `HARD_TRIP` classification.

## Promotion sequence

```text
SOURCE / TRACE: BD-001 CLOSED -> BD-002 CLOSED -> BD-003 CLOSED_CONTENT_TRACE_DOV
UTILITIES:      BD-004 CLOSED_SCOPE_RECONCILED -> BD-005 OPEN
CONTROLS:       BD-006 PARTIAL -> BD-007 when L2 evidence exists
GRAPH:          BD-008 after P0 engineering evidence is dispositioned
RENDER:         BD-009 v1.7
PUBLICATION:    BD-010 bind to existing #690/#691 carrier
```

## Non-compensating rules

A visual/navigation/publication PASS cannot grant engineering acceptance. Source age is not source invalidity. Later evidence cannot silently erase D2.1/D2.2 provenance. Source repetition is not transient validation. Controls cannot manufacture missing thermal or hydraulic evidence. Candidate I/O remains candidate until L2/detail design freezes it.

`GLOBAL_PROJECT_DOV = WITHHELD`.
