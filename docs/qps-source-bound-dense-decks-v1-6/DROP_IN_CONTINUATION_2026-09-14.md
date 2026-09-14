# QPS v1.6 — Drop-in continuation

Use this block to restart the next session without architecture rediscovery.

```text
Continue GBOGEB/CODEX QPS Visual Knowledge System from the 2026-09-14 v1.6.9 control handover.

READ FIRST:
- docs/qps-source-bound-dense-decks-v1-6/triage_v1_6.yaml
- docs/qps-source-bound-dense-decks-v1-6/SESSION_HANDOVER_2026-09-14.md
- docs/qps-source-bound-dense-decks-v1-6/DROP_IN_CONTINUATION_2026-09-14.md
- docs/qps-source-bound-dense-decks-v1-6/SESSION_PROGRESS_LEDGER_2026-09-14.yaml
- docs/qps-source-bound-dense-decks-v1-6/bd005_addendum_loop_boundary_v1_6.yaml
- docs/qps-source-bound-dense-decks-v1-6/d2_1_behavioral_lineage_v1_6.yaml
- docs/qps-source-bound-dense-decks-v1-6/d2_1_mode_state_matrix_v1_6.yaml
- docs/qps-source-bound-dense-decks-v1-6/graph_binding_overlay_v1_6.yaml
- docs/qps-source-bound-dense-decks-v1-6/source_vs_curated_dov_v1_6.yaml
- docs/qps-source-bound-dense-decks-v1-6/state_reconciliation_v1_6.yaml

HANDOVER REPRODUCTION CONTRACT:
- keep these same canonical current-state files synchronized after every bounded pulse or major prompt/reply tuple:
  1) triage_v1_6.yaml
  2) SESSION_HANDOVER_2026-09-14.md
  3) DROP_IN_CONTINUATION_2026-09-14.md
- append major conversation progression to SESSION_PROGRESS_LEDGER_2026-09-14.yaml.
- additive engineering/source evidence goes into dedicated ledgers; do not fork the handover framework.
- every merged major pulse ends with a post-merge read from main.

HARD RULES:
- do not restart architecture discovery;
- do not create another graph/render/publication/handover abstraction layer;
- do not overwrite prior deck/source versions;
- RENDER != SOURCE AUTHORITY;
- VISUAL PASS != ENGINEERING PASS;
- DOCUMENT POLISH != ACCEPTANCE CREDIT;
- D2.1 is PROCESS CONCEPTUAL DESIGN anchor;
- D2.2 is TECHNICAL + PROJECT REQUIREMENTS anchor;
- current Addendum II requirements refine the contractual tender boundary without erasing D2.1/D2.2 provenance;
- derivative requirement tables cannot override authoritative Addendum numbering/content;
- process fallback semantics do not automatically define SIL/MIS/MIT/HARD_TRIP;
- source-text mode extraction does not substitute for per-diagram valve/colour proof;
- use #690/#691 for generic publication;
- global/project DoV remains WITHHELD.

CURRENT BD QUEUE:
- BD-001 CLOSED.
- BD-002 CLOSED.
- native source text CLOSED.
- BD-003 CLOSED_CONTENT_TRACE_DOV.
- BD-004 CLOSED_SCOPE_RECONCILED.
- BD-005 OPEN — CONTRACTUAL LOOP BOUNDARY SHARPENED; executable selected-equipment/hydraulic/thermal transient inputs remain open.
- BD-006 PARTIAL_EVIDENCE_BOUND.
- BD-007 OPEN_L2_GATED.
- BD-008 PREPARED_P0_GATED.
- BD-009 DEFER_TO_V1_7.
- BD-010 REFRAME_BIND_EXISTING_CARRIER — #690/#691.

BD-005 CONTRACTUAL LOOP BOUNDARY:
- RTM-401: up to 350 kW backup diesel power after an interruption of a few minutes; NOT automatically one-HP allocation.
- RTM-428: up to 350 kW backup PCW after a few minutes; hydraulically common WCS header; reduced total flow allowed.
- RTM-432/433: no continuous normal IA during LOOP beyond initial actuations; QPS pneumatic backup autonomy = 6 h under full helium-recovery load.
- RTM-434/435: dedicated HP exhaust ducts; steady-state WCS room-air heat <=120 kW; at least 50% direct to exhaust ducts.
- RTM-436: during LOOP HP exhaust ducts remain available without restriction; compressor-room ambient heat <=15 kW.
- RTM-258/260/261/262: limited services for recovery; abnormal QRB.S return >=100 g/s; recovery to normal circulation required.
- bidder ~110 g/s with one emergency compressor remains REVIEW_REQUIRED evidence, not accepted contractual operating point.
- 72 Hz / ~112 g/s / ~357 kW remains maximum reference; do not linearly scale power/CW into the selected LOOP point.
- 6 h pneumatic autonomy is NOT proof of the working ~6 h thermal stabilization statement.

D2.1 BEHAVIORAL EDGE LANE:
- Appendix 8.2 = General PFD / topology.
- Appendix 8.3 = SIMCRYOGENICS / conceptual process physics and model lineage.
- Appendix 8.4 = MODES / valve-state, fallback, available-path and process-transition evidence.
- d2_1_mode_state_matrix_v1_6.yaml binds cooldown, warmup, purge/fill, vacuum-loss cases, minor QCELL fault, quench, loss of utility and cryoplant trip.
- CV503 = source-bound cooldown bottom-helium circulation function.
- HV510/HV520 = source-bound local manual purge/fill function.
- Green/color visual semantics must be decoded per diagram/legend.

SANITIZED D2.1:
- user reports a slightly sanitized D2.1 with LKT/ALAT references removed.
- indexed native Library candidate is NOT proven to be that sanitized copy; bind exact sanitized derivative by file/version/hash when surfaced.

BD-005 FIRST-RED INPUTS:
1. current OEM/contractor HP operating point near selected ~110 g/s: Hz, kW, CW rejection;
2. ES02 auxiliary load split and margin within up-to-350-kW backup boundary;
3. actual PAB12 LOOP flow, pressure, temperatures, pump/fan power, valve state;
4. OFFER-35 HP duct size, flow rate and allowable pressure drop;
5. quantitative HV03 degraded room airflow/heat-removal state or model proof that RTM-436 duct path + <=15 kW ambient ceiling is sufficient;
6. effective free room volume + equipment/building thermal mass;
7. physical variable/limit behind working ~2 h onset;
8. measurable thermal criterion behind working ~6 h stabilization, separate from IA autonomy;
9. first-law WCS transient + uncertainty + independent review.

BD-008 PARALLEL NEXT:
- enumerate Appendix 8.4 diagram/page -> mode mapping;
- bind visible valve tags/states where exact reading is supported;
- bind per-diagram colour/state convention;
- compare visual state against source-text mode matrix;
- keep engineering acceptance gated by BD-005/006.

MAJOR-TUPLE UPDATE LOOP:
user major prompt
-> execute bounded work
-> append progression ledger entry
-> refresh evidence ledger(s)
-> refresh TRIAGE + full handover + drop-in
-> verify W003 + qps-canonicalization
-> merge with non-compensating state
-> post-merge read from main
-> continue in same chat unless user requests handoff/closure.

IMMEDIATE ACTION:
Continue here. Acquire the current selected ~110 g/s HP operating point, ES02 split, PAB12 degraded hydraulic state and OFFER-35 duct data. Do not execute/credit the first-law transient until those inputs are evidence-bound. In parallel, continue Appendix 8.4 graph extraction without closing BD-005/006.
```
