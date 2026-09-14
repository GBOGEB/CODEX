# QPS v1.6 — Drop-in continuation

Use this block to restart the next session without architecture rediscovery.

```text
Continue GBOGEB/CODEX QPS Visual Knowledge System from the 2026-09-14 v1.6.10 control handover.

READ FIRST:
- docs/qps-source-bound-dense-decks-v1-6/triage_v1_6.yaml
- docs/qps-source-bound-dense-decks-v1-6/SESSION_HANDOVER_2026-09-14.md
- docs/qps-source-bound-dense-decks-v1-6/DROP_IN_CONTINUATION_2026-09-14.md
- docs/qps-source-bound-dense-decks-v1-6/SESSION_PROGRESS_LEDGER_2026-09-14.yaml
- docs/qps-source-bound-dense-decks-v1-6/bd005_addendum_loop_boundary_v1_6.yaml
- docs/qps-source-bound-dense-decks-v1-6/bd005_current_lkt_fsd575_loop_point_v1_6.yaml
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
- a major tuple changes evidence/lineage, BD state/priority, source authority/currentness, first-red/execution sequence, graph semantics, handover contract, or material PR/merge restart context.
- minor no-state-change turns may be folded into the next major tuple to avoid noisy commits.
- every merged major pulse ends with a post-merge read from main.

HARD RULES:
- do not restart architecture discovery;
- do not create another graph/render/publication/handover abstraction layer;
- do not overwrite prior deck/source versions;
- RENDER != SOURCE AUTHORITY;
- VISUAL PASS != ENGINEERING PASS;
- DOCUMENT POLISH != ACCEPTANCE CREDIT;
- preserve explicit source identities, hashes, dispositions and receipts;
- D2.1 is the PROCESS CONCEPTUAL DESIGN anchor;
- D2.2 is the TECHNICAL + PROJECT REQUIREMENTS anchor;
- current Addendum II requirements refine the contractual tender boundary without erasing D2.1/D2.2 provenance;
- current bidder maximum/equipment data do not automatically become the proven LOOP operating point;
- source age/maturity is separate from provenance/evidence authority;
- derivative requirement tables cannot override authoritative Addendum numbering/content;
- process fallback semantics do not automatically define SIL/MIS/MIT/HARD_TRIP;
- source-text mode extraction does not substitute for per-diagram valve/colour proof;
- historical tuple summaries never override stronger current TRIAGE/evidence;
- use #690/#691 for generic publication; do not create a duplicate QPS exporter;
- global/project DoV remains WITHHELD.

CURRENT BD QUEUE:
- BD-001 CLOSED — exact source bytes bound.
- BD-002 CLOSED — 63 source renders bound.
- native source text CLOSED — 63 slide identities bound independently of OCR.
- BD-003 CLOSED_CONTENT_TRACE_DOV — 63/63 explicit disposition, zero silent drops, five lineage repairs.
- BD-004 CLOSED_SCOPE_RECONCILED — 1199/~1200/1256/1300 kW semantic scopes only.
- BD-005 OPEN — CURRENT SELECTED FSD575 MAX POINT / EPS ROUTING / AIR-SIDE BOUND; exact <=350 kW LOOP point, Recovery Cooling Water and thermal transient inputs remain open.
- BD-006 PARTIAL_EVIDENCE_BOUND — tender-level + D2.1 fallback/mode semantics; discipline cause/effect remains open.
- BD-007 OPEN_L2_GATED.
- BD-008 PREPARED_P0_GATED — source mode/state matrix bound; diagram/valve/colour visual extraction and P0 engineering edges remain unresolved.
- BD-009 DEFER_TO_V1_7.
- BD-010 REFRAME_BIND_EXISTING_CARRIER — #690/#691.

D2.1 BEHAVIORAL EDGE LANE:
- Appendix 8.2 = General PFD / topology.
- Appendix 8.3 = SIMCRYOGENICS / conceptual process physics and model lineage.
- Appendix 8.4 = MODES / valve-state, fallback, available-path and process-transition evidence.
- d2_1_mode_state_matrix_v1_6.yaml binds cooldown, warmup, purge/fill, vacuum-loss cases, minor QCELL fault, quench, loss of utility and cryoplant trip.
- CV503 = source-bound cooldown bottom-helium circulation control function.
- HV510/HV520 = source-bound local manual purge/fill function.
- Minor QCELL fault = supply close / return open; supply NC / return NO as conceptual fallback.
- Loss of utility = cryosystem stop; fallback; cryoplant interfaces close; QVB close except NO returns.
- Cryoplant trip = similar fallback; at least one compressor restart is a source recovery path.
- Green/color visual semantics must be decoded per diagram/legend; do not globally equate colour with OPEN/CLOSED.

SANITIZED D2.1:
- user reports a slightly sanitized D2.1 with LKT/ALAT references removed.
- the currently indexed native Library candidate is NOT proven to be that sanitized copy: no exact LKT match was found, but one ALaT reference remains in the reference list.
- bind the sanitized derivative by exact file/version/hash when surfaced; never infer identity from a similar title.

PRIOR BD-005 FIRST-RED INPUT SUPERSET (retained for lossless history):
1. current revision/change lineage without deleting D2.1/D2.2 provenance;
2. current OEM/contractor WCS dissipated-heat schedule;
3. one-HP emergency electrical/VFD point + ES02 auxiliary split;
4. PAB12 emergency PCW flow/pressure/temperatures/pump-fan power/valve state;
5. HV03 degraded/LOOP airflow/fan/heat-removal state;
6. ducting boundary for 17.4/14.2/5.7 kW paths;
7. effective room volume + equipment/building thermal mass;
8. physical variable/limit behind ~2 h onset;
9. measurable criterion behind ~6 h stabilization;
10. first-law WCS transient + uncertainty + independent review.

V1.6.9 CONTRACTUAL LOOP DELTA (retained):
- RTM-401: up to 350 kW backup diesel power after a few minutes; NOT proof of full one-HP allocation.
- RTM-428: up to 350 kW backup PCW after a few minutes; common WCS header; reduced total flow allowed.
- RTM-432/433: six-hour requirement = pneumatic backup autonomy under full helium-recovery load, NOT thermal stabilization proof.
- RTM-434/435: dedicated HP exhaust ducts; steady-state WCS room-air heat <=120 kW; at least 50% direct to ducts.
- RTM-436: LOOP HP exhaust ducts remain available without restriction; compressor-room ambient heat <=15 kW.
- RTM-258/260/261/262: limited-service recovery; abnormal QRB.S return >=100 g/s; recovery to normal circulation required.
- derivative Support System ICD RTM labels are navigation clues only where they conflict with authoritative Addendum II.

V1.6.10 CURRENT LKT / FSD575 DELTA:
- current bidder source = LKT - Offer 1.pdf, Issue 01, 2026-08-10, SHA256 d92af4666cc10ec6a4f8ac6cfe57aef477bca116f72a12f9156a680ce7e1e35e.
- current selected HP fleet = 4 x KAESER FSD575 SFC water-cooled.
- current maximum point = 112.0 g/s (-2/+5%) at 14 bara / 72 Hz; package power = 357 kW +/-5%.
- EPS power limitation = 350 kW.
- two main compressors are connected to EPS, but generator size permits only one to operate during LOOP.
- bidder LOOP claim = up to approximately 110 g/s with one emergency-powered compressor.
- exact ~110 g/s Hz/power point is NOT stated; no linear interpolation credit.
- current normal compressor cooling water = 4 x 18.5 m3/h; 3-8 barg; 20-30 C supply; <=45 C return; <=15 K rise.
- Recovery Cooling Water without glycol = explicitly TO BE DEFINED in current Basis of Process Design; normal 18.5 m3/h is NOT promoted to PAB12 LOOP flow.
- selected-package cooling air = 5000 m3/h main + 4200 m3/h SFC; maximum added duct pressure drop = 40 Pa.
- current heat paths = 17.4 kW compressor cooling air + 10.7 kW SFC cooling air + 13.9 kW ambient radiation.
- 13.9 kW is below the RTM-436 <=15 kW ambient ceiling but does NOT replace installed duct or room-transient proof.
- OFFER-35 points HP compressor response to Technical Part Chapter 6; flow and allowable pressure drop are source-bound.
- TAX06 locates/dimensions cooling-air interfaces, but no single unambiguous duct connection size has been promoted.
- exhaust ducting remains Contracting Authority scope; current offer requires exhaust cooling air to be led outside the compressor room.

CURRENT BD-005 FIRST-RED:
1. exact bidder/OEM LOOP Hz / flow / package-power point that delivers ~110 g/s with adequate margin inside 350 kW EPS;
2. complete ES02 critical auxiliary load split and simultaneity;
3. actual PAB12 / Recovery Cooling Water LOOP flow, pressure, temperatures, pump/fan power and valve state — presently TO BE DEFINED;
4. unambiguous OFFER-35 duct connection size / vendor connection specification;
5. effective free room volume + equipment/building thermal mass;
6. quantitative degraded HV03 room airflow/heat-removal state or proof that installed duct path + <=15 kW ambient boundary is sufficient;
7. physical variable/limit behind working ~2 h onset;
8. measurable thermal criterion behind working ~6 h stabilization, separate from pneumatic autonomy;
9. first-law WCS transient + uncertainty + independent review.

NON-COMPENSATING BD-005 RULES:
- selected FSD575 maximum point != proven LOOP operating point.
- 357 kW +/-5% at 112 g/s does not prove margin inside 350 kW EPS.
- two compressors connected to EPS != two simultaneously operating during LOOP.
- 18.5 m3/h normal per-compressor CW != Recovery Cooling Water / PAB12 LOOP flow.
- 13.9 kW ambient radiation below 15 kW contractual ceiling != room transient closure.
- OFFER-35 airflow + 40 Pa != duct connection-size closure.

PR714 GOVERNANCE EXECUTION RECEIPT:
- PR #714 merged at 1bc865a07c1c57e951b2c1d2633c45ab419aafa4; metrics main head became cab4ffcb85c0a6cbcaa8a6fb1cef790a5dfdece4.
- qps-canonicalization on the PR #714 head = PASS.
- W003 on the PR #714 head = FAIL PR-007 because the PR classification block omitted the required literal --- delimiter.
- failure scope = PR metadata parser only; engineering evidence effect = NONE.
- #714 merged concurrently before a fresh W003 recheck.
- PR body was repaired post-merge to include the required delimiter.
- follow-up governance receipt PR must pass W003 + qps-canonicalization; no BD or engineering state moves from this control repair.

BD-008 PARALLEL NEXT:
- enumerate Appendix 8.4 diagram/page -> mode mapping;
- bind visible valve tags/states where source resolution supports exact reading;
- bind per-diagram colour/state convention;
- compare visual state against source-text mode matrix and flag contradictions;
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

3PR NEXT:
P1 Recover exact new evidence and current main head.
P2 Reconcile source authority, currentness and contradictions without normalization.
P3 Re-enter only proven semantic/source edges; keep engineering edges gated.

MIP NEXT:
Modernize stale/misaligned state only.
Innovate with bounded alternate edges/models and explicit metrics.
Perpetuate by updating the SAME canonical TRIAGE/full-handover/drop-in files plus append-only progression and additive evidence ledgers.

IMMEDIATE ACTION:
First close the PR #714 governance receipt with W003 + qps-canonicalization both green. Then resume the exact LKT/KAESER ~110 g/s <=350 kW LOOP operating-point hunt, in parallel with Recovery Cooling Water/PAB12 degraded hydraulics and current duct connection size. Do not execute or credit the first-law transient until electrical, hydraulic and thermal-inventory inputs are evidence-bound. Keep BD-006 and BD-008 non-compensating.
```