# QPS Visual Knowledge System — Lossless Session Handover

Date: 2026-09-14
Current control version: `v1.6.11`
Repository: `GBOGEB/CODEX`
Scope: QPS v1.6 source-bound Utilities / Controls / Naming / LOOP / graph lineage
Authority: `ENGINEERING_CURATION_NOT_DESIGN_APPROVAL`
Global/project DoV: `WITHHELD`

## 1. Session result

This session moved QPS v1.6 from source-identity uncertainty to a controlled source/content lineage with explicit engineering first-reds and a reproducible drop-in restart contract.

Closed source/curation predicates:

- BD-001 exact source PPTX bytes bound.
- BD-002 stable renders bound for all 63 selected source slides.
- native source text independently bound for the same 63 slide identities.
- BD-003 closed as `CLOSED_CONTENT_TRACE_DOV` with 63/63 explicit KEEP/MERGE/REFERENCE/SUPERSEDE dispositions and zero silent drops.
- BD-003 also repaired five concrete lineage errors in Utilities / Controls / Naming mappings.
- BD-004 closed as `CLOSED_SCOPE_RECONCILED` for the 1199 / ~1200 / 1256 / 1300 kW scope labels only; no facility-sizing approval was created.

Engineering predicates remain non-compensating and open where evidence is incomplete.

## 2. Source authority model

The controlling distinction is:

`TEMPORAL MATURITY != PROVENANCE / EVIDENCE AUTHORITY`

### D2.1

D2.1 is the **process conceptual design anchor**. It carries:

- process architecture and topology;
- process/model assumptions and SIMCRYOGENICS lineage;
- normal, transient and abnormal process behavior;
- PFD state and valve/fallback semantics through Appendix 8.4.

D2.1 remains an aged active anchor. Later design evolution creates traceable refinement/deviation/change edges; it does not erase D2.1 provenance.

The Library native candidate `D2_1_CRYOGENIC_SYSTEM_CONCEPTUAL_NATIVE.docx` is not declared to be the user's sanitized derivative because one ALaT reference remains in its references section. The sanitized derivative shall be bound as a distinct file/version/hash identity when surfaced.

### D2.2

D2.2 is the **technical and project requirements anchor**. It carries technical constraints, project requirements, interface/test requirements and project boundary conditions. It does not replace D2.1 process behavior.

## 3. D2.1 behavioral lineage recovered

D2.1 Appendix 8.2 / 8.3 / 8.4 are treated as three separate evidence lanes:

1. `8.2 General PFD` — process topology.
2. `8.3 SIMCRYOGENICS` — conceptual process-physics/model lineage.
3. `8.4 MODES` — behavioral state / transition / valve-alignment evidence.

The D2.1 text explicitly states that transient modes are implemented on the Process Flow Diagram and compiled in a dedicated diagrams ZIP. Appendix 8.4 therefore supplies graph-edge behavior, not merely presentation images.

Explicit process-behavior examples retained:

- minor QCELL fault: supply valves close, return valves remain open; supply valves are normally closed and returns normally open to preserve/recover helium;
- loss of utility: cryogenic system stops, components go to fallback, cryoplant interface valves close, QVB valves close except normally-open returns;
- cryoplant trip: similar fallback behavior to loss of utility; restart of at least one compressor supports helium recovery/storage;
- quench: conceptual proposal to keep TS/coupler cooling as long as possible, close superfluid supply and allow VLP return pressure control.

These are process-concept behavior edges. They are not a frozen cause/effect matrix and do not by themselves assign MIS/MIT class, SIL, or HARD_TRIP.

## 4. v1.6.7 bounded pulse — source mode/state matrix

The latest pulse adds `d2_1_mode_state_matrix_v1_6.yaml` and advances BD-008 source extraction without granting engineering credit.

Source-bound mode families now include:

- cool-down sequence;
- warm-up sequence;
- purge/fill;
- distribution vacuum loss;
- single-QM vacuum loss;
- minor QCELL fault;
- quench proposal;
- loss of utility;
- cryoplant trip.

Named valve behavior now source-bound at text level includes:

- `CV503`: controls bottom helium supply used for cavity gas circulation during cool-down;
- `HV510` / `HV520`: local manual purge/fill hand valves;
- minor QCELL fault: supply `NC` / return `NO` process fallback semantics;
- loss of utility / cryoplant trip: `NO` paths open and `NC` paths close according to the conceptual fallback description.

This is a **source mode/state matrix**, not a final cause/effect matrix. Exact Appendix 8.4 diagram-to-mode mapping, visible valve-state extraction and colour-legend decoding remain open. Green or another drawing colour is not globally equated to OPEN/CLOSED until the relevant diagram or legend proves it.

## 5. BD queue at session close before v1.6.9 refinement

| ID | Priority | State | Session-close meaning |
|---|---|---|---|
| BD-001 | P0 | CLOSED | exact source bytes bound |
| BD-002 | P0 | CLOSED | 63 source renders bound |
| native-text binding | P0 | CLOSED | native text bound to same slide identities |
| BD-003 | P0 | CLOSED_CONTENT_TRACE_DOV | 63/63 reviewed, zero silent drop; five lineage repairs |
| BD-004 | P0 | CLOSED_SCOPE_RECONCILED | utilities value scopes reconciled only |
| BD-005 | P0 | OPEN | D2.1/D2.2 anchors and several LOOP values bound; degraded WCS boundary + executable first-law transient still missing |
| BD-006 | P0 | PARTIAL_EVIDENCE_BOUND | tender-level classifications plus D2.1 fallback semantics; discipline cause/effect remains open |
| BD-007 | P1 | OPEN_L2_GATED | detailed I/O awaits L2/detail design |
| BD-008 | P1 | PREPARED_P0_GATED | source/lineage graph overlay prepared; engineering closure gated by BD-005/006 and per-mode valve extraction |
| BD-009 | P1 | DEFER_TO_V1_7 | deterministic render after engineering/graph stabilization |
| BD-010 | P1 | REFRAME_BIND_EXISTING_CARRIER | reuse merged #690/#691 publication carrier |

## 6. First-red and TODO before v1.6.9 refinement

### P0 — BD-005 LOOP / degraded state

Close only after the following are evidence-bound:

1. current approved revision/change lineage while retaining D2.1/D2.2 provenance;
2. current contractor/OEM WCS dissipated-heat schedule;
3. exact one-HP emergency electrical/VFD operating point and ES02 auxiliary split;
4. PAB12 emergency PCW flow, pressure, supply/return temperatures, pump/fan power and valve state;
5. quantitative HV03 degraded/LOOP airflow, fan power and heat-removal state;
6. package/VFD ducting boundary for 17.4 / 14.2 / 5.7 kW heat paths;
7. effective free room volume and equipment/building thermal mass;
8. physical variable and limit behind the `~2 h` onset statement;
9. measurable stabilization criterion behind `~6 h`;
10. first-law WCS LOOP transient with uncertainty and independent review.

D2.1 Line-S transient evidence is a separate lane and must not be used as a substitute for the WCS-room thermal model.

### P0 — BD-006 Controls

Only close classifications when discipline evidence proves:

- cause/effect;
- fail-safe / loss-of-signal behavior;
- exact protocol/owner boundary;
- trip/permissive consequence;
- relevant L2 I/O allocation.

D2.1 fallback valve behavior strengthens process semantics but does not automatically create a hard trip.

### P1 — BD-008 graph

Use the existing v1.5 graph carrier. Bind the new overlay additively:

- D2.1 -> Appendix 8.2 topology;
- D2.1 -> Appendix 8.3 physics/model lineage;
- D2.1 -> Appendix 8.4 behavior/state;
- D2.2 -> requirement/constraint edges;
- OPEN BD-005/006 edges remain visibly OPEN.

Next graph extraction task: decode Appendix 8.4 per-mode valve states and legends, especially green-highlighted paths, without assuming globally that green means open until each drawing/legend proves that meaning.

## 7. 3PR receipt through v1.6.8

### P1 — Recover

Recovered and re-read current source identity, current `main` TRIAGE, v1.5 graph carrier, D2.1 native conceptual-design text, Appendix 8.4 mode pages, and source-vs-curated lineage.

### P2 — Reconcile / prove

Reconciled:

- D2.1 process-concept role vs D2.2 requirement role;
- aged source status vs retained provenance authority;
- WCS-room LOOP transient vs Line-S cryogenic-return transient;
- v1.5 graph carrier vs richer v1.6 semantic overlay;
- sanitized derivative identity vs unsanitized/native source candidate;
- source-text mode behavior vs still-open per-diagram colour/valve visual proof.

No engineering acceptance was promoted by semantic reconciliation.

### P3 — Re-enter

Re-entry is accepted only at the source/lineage layer:

- D2.1 behavioral lineage and source mode/state matrix may enter the graph overlay now;
- BD-008 remains `PREPARED_P0_GATED`, not CLOSED;
- engineering-dependent edges remain gated by BD-005/006;
- global/project DoV remains WITHHELD.

## 8. MIP receipt through v1.6.8

### Modernize

- repaired stale source-role language;
- separated temporal age from source authority;
- separated process-concept behavior from project requirements;
- reused the existing graph carrier instead of creating a second graph architecture;
- preserved the retained-evidence precedence rule after the #700 stale-state collision.

### Innovate

- introduced a behavioral-edge evidence lane from D2.1 Appendix 8.4;
- added a source-derived mode/state matrix with explicit named-valve behavior where text supports it;
- represented fallback/path semantics as overlay metadata projected onto existing `tree/interface/control` edge types;
- separated WCS-room thermal survival from Line-S cryogenic return behavior so each can mature independently.

### Perpetuate

- source/provenance and engineering-acceptance states remain explicitly separate;
- OPEN edges remain OPEN in graph publication;
- the sanitized D2.1 derivative requires its own exact file/version identity;
- deterministic rendering remains deferred until graph/engineering stability;
- governed publication continues through #690/#691 rather than a QPS-specific duplicate exporter;
- the same canonical TRIAGE, full handover and drop-in files are refreshed after each bounded pulse.

## 9. Lossless reproduction contract

To keep the handover current without creating another framework, every subsequent bounded pulse shall update these **same three canonical outputs**:

1. `triage_v1_6.yaml` — machine-readable current state, BD queue, evidence pointers and non-compensating gates.
2. `SESSION_HANDOVER_2026-09-14.md` — full human-readable lossless state and lineage.
3. `DROP_IN_CONTINUATION_2026-09-14.md` — compact restart block that is safe to paste into a new session.

The append-only progression surface is:

4. `SESSION_PROGRESS_LEDGER_2026-09-14.yaml`

Additive evidence should remain in dedicated ledgers such as `d2_1_mode_state_matrix_v1_6.yaml`; do **not** duplicate the handover architecture.

Reproduction sequence:

```text
read TRIAGE
→ read full handover
→ read drop-in restart
→ read progression ledger
→ read only evidence files named by current TRIAGE
→ execute first-red / parallel lanes
→ refresh evidence ledger(s)
→ append major tuple progression entry
→ refresh TRIAGE + full handover + drop-in in the same PR
→ verify canonicalization/governance gates
→ merge
→ post-merge read from main
```

This makes the session state reproducible from repository truth without relying on chat memory.

## 10. Major prompt/reply tuple progression contract

A tuple is **major** when it changes evidence/source lineage, BD state/priority/close predicate, source authority/currentness interpretation, first-red/execution sequence, graph/behavior semantics, the handover contract, or material PR/merge context needed for restart.

After each major tuple:

- append one progression-ledger entry capturing user intent, executed delta, repository receipt, BD movement/non-movement and DoV/credit boundary;
- refresh the same three canonical current-state outputs in the same bounded PR;
- preserve additive engineering/source ledgers separately;
- verify governance/canonicalization gates where applicable;
- post-merge read from `main`.

Minor acknowledgements or wording-only turns with no state/evidence/sequence delta may be folded into the next major tuple to avoid meaningless repository churn.

The progression ledger explains how the current state was reached but never overrides stronger current TRIAGE/evidence.

## 11. Non-compensating controls

- `RENDER != SOURCE AUTHORITY`
- `VISUAL PASS != ENGINEERING PASS`
- `DOCUMENT POLISH != ACCEPTANCE CREDIT`
- source/content DoV does not validate open engineering claims;
- source age is not source invalidity;
- source-text mode extraction is not per-diagram valve/colour proof;
- green/color semantics require per-drawing legend/state binding;
- process fallback semantics do not automatically assign SIL or HARD_TRIP;
- candidate I/O remains candidate until L2/detail design;
- historical tuple summaries do not override stronger current evidence;
- global/project DoV remains `WITHHELD`.

## 12. Restart victory condition before v1.6.9 refinement

The next high-value victory was one of:

- obtain enough BD-005 degraded-state inputs to execute the first defensible WCS-room first-law transient; or
- obtain discipline cause/effect evidence that closes one real BD-006 classification conflict.

In parallel, Appendix 8.4 diagram/valve/colour extraction may continue as source/lineage work, but it cannot bypass those P0 engineering gates.

## 13. v1.6.9 current delta — Addendum II contractual LOOP boundary

This section is additive and updates the current interpretation without deleting the earlier evidence/history above.

`bd005_addendum_loop_boundary_v1_6.yaml` binds the authoritative Addendum II degraded-utility constraints:

- **RTM-401:** up to 350 kW backup diesel power after an interruption of a few minutes; this is a power boundary, not proof that one HP compressor may consume the full 350 kW.
- **RTM-428:** up to 350 kW backup cooling-water capacity after a few minutes; common WCS header; reduced total flow is allowed.
- **RTM-432 / RTM-433:** normal continuous IA is not available during LOOP beyond initial actuations; QPS pneumatic backup shall support helium recovery for **6 h under full recovery load**.
- **RTM-434 / RTM-435:** dedicated HP exhaust ducts are part of the HVAC boundary; steady-state WCS heat to room air is limited to 120 kW and at least 50% is transferred directly to those ducts.
- **RTM-436:** during LOOP the HP exhaust ducts remain available without restriction and compressor-room ambient heat is limited to **≤15 kW**.
- **RTM-258 / 260 / 261 / 262:** limited services support helium recovery; abnormal QRB.S return capability is **≥100 g/s** and normal circulation recovery is required.

Critical reconciliations:

- the source `6 h` requirement above is **pneumatic autonomy**, not proof of the separate working `~6 h` thermal-stabilization statement;
- the historical `~17 kW` path remains provenance, while the contractual LOOP ambient-room design ceiling is now `≤15 kW`;
- bidder `~110 g/s` with one emergency compressor remains `REVIEW_REQUIRED` evidence;
- `72 Hz / ~112 g/s / ~357 kW` remains an equipment-maximum reference and is not linearly scalable into the selected LOOP point;
- the derivative Support System ICD sheet is retained as a navigation clue only where its RTM numbering diverges from Addendum II.

### Current BD-005 state at v1.6.9

`CONTRACTUAL_LOOP_BOUNDARY_SHARPENED_EXECUTABLE_TRANSIENT_INPUTS_OPEN`

Newly closed subquestions are contractual backup-power ceiling/delay, backup-PCW thermal ceiling/common-header degraded-flow allowance, pneumatic-autonomy scope, LOOP ambient-room heat ceiling, HP exhaust-duct availability, and contractual abnormal QRB.S minimum flow.

### First-red after v1.6.9

1. current OEM/contractor HP operating point at selected `~110 g/s`: Hz, kW, cooling-water rejection;
2. ES02 auxiliary split and margin within the up-to-350-kW backup boundary;
3. actual PAB12 LOOP flow/pressure/temperatures/pump-fan power/valve state;
4. OFFER-35 HP duct size, flow rate and allowable pressure drop;
5. quantitative HV03 degraded room airflow/heat-removal state, or model proof that the RTM-436 duct path plus `≤15 kW` ambient ceiling is sufficient;
6. effective free room volume and equipment/building thermal mass;
7. physical variable/limit behind working `~2 h` onset;
8. measurable thermal criterion behind working `~6 h` stabilization, kept separate from IA autonomy;
9. first-law WCS transient with uncertainty and independent review.

BD-006 remains `PARTIAL_EVIDENCE_BOUND`; BD-008 remains `PREPARED_P0_GATED`; global/project DoV remains `WITHHELD`.

## 14. v1.6.10 current delta — direct current LKT FSD575 / EPS / OFFER-35 evidence

This section is additive. It supersedes only the uncertainty identified in the v1.6.9 first-red where direct current bidder evidence has now been recovered; it does not delete the earlier state/history.

New evidence ledger: `bd005_current_lkt_fsd575_loop_point_v1_6.yaml`.

### Direct current bidder selection and maximum point

The current LKT Offer 1 directly selects **four KAESER FSD575 SFC water-cooled compressors**. The current technical table gives, for one selected package:

- motor rated power: **315 kW**;
- suction: **1.05 bara / 298 K**;
- discharge design condition: **14 bara**;
- maximum helium flow: **112.0 g/s (-2/+5%) at 72 Hz**;
- package power input at that point: **357 kW ±5%**.

This is now current bidder evidence; the historical/prestudy bridge is no longer needed to establish the selected model or the 72 Hz maximum point.

It is still **not** the proven LOOP operating point because the current bidder also sets the emergency-power limitation at **350 kW** and separately claims maximum LOOP recovery of approximately **110 g/s**. No exact bidder/OEM Hz + power value for that lower LOOP point has yet been found, and linear scaling remains prohibited as acceptance proof.

### EPS topology reconciled

The current proposal interface table says emergency supply is provided for at least two compressors. OFFER-22 resolves the apparent contradiction:

- **two main compressors are connected to emergency power**;
- because of diesel-generator size, **only one compressor can operate** during LOOP;
- the claimed abnormal/LOOP S-line recovery capacity is **up to approximately 110 g/s** with that one compressor.

Therefore the former “one vs two compressor” architectural conflict is closed as **redundant electrical connection / single simultaneous operation**. The remaining electrical first-red is quantitative: prove the exact one-compressor LOOP operating point and total EPS load margin inside 350 kW.

The preliminary single-line diagram exposes approximately **500 W UPS per compressor** for local control but leaves the main required-power field unresolved; it is not a complete ES02 critical-load list.

### Current cooling-air / OFFER-35 evidence

The selected current FSD575 table binds:

- main cooling air: **5000 m³/h**;
- SFC cooling air: **4200 m³/h**;
- maximum additional duct pressure drop: **40 Pa**;
- compressor cooling-air heat: **17.4 kW**;
- SFC cooling-air heat: **10.7 kW**;
- ambient radiation: **13.9 kW**;
- heat-recovery branch at max load: **229 kW at 7.9 m³/h for ΔT 25°C**.

The OFFER-35 response explicitly points the HP-compressor answer to Technical Part Chapter 6. Thus **airflow and allowable pressure drop are now current-source-bound**. TAX06 shows the cooling-air inlet/outlet interface locations and dimensions, but no single unambiguous duct-connection size has been promoted; that geometry remains open.

The current technical proposal also places exhaust ducting in Contracting Authority scope and requires compressor exhaust cooling air to be led outside the compressor room.

The **13.9 kW ambient-radiation term** is numerically below the contractual RTM-436 LOOP ambient-room ceiling of **≤15 kW**, but this is not a room-transient closure. The 17.4/10.7 kW terms are explicitly cooling-air paths; installed routing, effective room thermal mass and degraded-room/HV03 behavior still require proof.

### Current cooling-water evidence

The current normal utility table gives compressor cooling water as **4 × 18.5 = 78 m³/h**, with:

- supply pressure **3–8 barg**;
- supply temperature **20–30°C**;
- return temperature **≤45°C**;
- temperature rise **≤15 K**.

This is a current **normal** per-compressor reference, not a LOOP/PAB12 hydraulic state. The current Basis of Process Design explicitly marks **Recovery Cooling Water without glycol: TO BE DEFINED**. That statement is stronger than any inference from the normal 18.5 m³/h value and keeps PAB12 degraded hydraulics open.

### Current BD-005 state after v1.6.10

`CURRENT_SELECTED_MODEL_MAX_POINT_EPS_ROUTING_AND_AIRSIDE_BOUND_EXECUTABLE_LOOP_POINT_OPEN`

Newly closed subquestions:

- selected current HP compressor model;
- current 72 Hz maximum flow/power reference;
- main/SFC cooling-air flows;
- allowable added duct Δp;
- current air-side heat-path split;
- normal per-compressor cooling-water reference;
- two-EPS-connected vs one-running semantics;
- OFFER-35 airflow and allowable pressure-drop response.

### Sharpened first-red after v1.6.10

1. obtain bidder/OEM confirmation of the exact **LOOP Hz / flow / package-power point** that delivers approximately 110 g/s with adequate margin inside the 350 kW EPS limit;
2. bind the complete **ES02 critical auxiliary load split and simultaneity**;
3. bind actual **PAB12 / Recovery Cooling Water** flow, pressure, supply/return temperatures, pump/fan power and valve state — currently explicitly `TO BE DEFINED`;
4. bind an unambiguous **OFFER-35 duct connection size / vendor connection specification**;
5. bind effective room/equipment thermal mass and free/effective air volume;
6. bind quantitative degraded HV03/room airflow, or prove that the installed duct path plus ambient boundary is sufficient for the selected thermal model;
7. define the physical variable/limit behind working `~2 h` onset;
8. define the measurable thermal criterion behind working `~6 h` stabilization without conflating it with six-hour pneumatic autonomy;
9. only then execute the first-law WCS LOOP transient with uncertainty and independent review.

BD-006 remains `PARTIAL_EVIDENCE_BOUND`; BD-008 remains `PREPARED_P0_GATED`; global/project DoV remains `WITHHELD`.

## 15. TUPLE-006 governance execution receipt — PR #714 / corrective PR #717

PR #714 merged at `1bc865a07c1c57e951b2c1d2633c45ab419aafa4`; the subsequent metrics receipt moved `main` to `cab4ffcb85c0a6cbcaa8a6fb1cef790a5dfdece4`.

The engineering evidence in v1.6.10 is unchanged by the following control exception:

- `qps-canonicalization` passed on the PR #714 head;
- `W003 Governance Gate` failed with `PR-007` because the pull-request classification block omitted the literal `---` delimiter required by the metadata parser;
- PR #714 was merged concurrently before a fresh W003 recheck could run;
- corrective PR #717 preserved the exception transparently;
- #717 first failed because `PR-ID` was required, then because `SCHEMA MUTATION: NONE` was not an allowed enum;
- the header was repaired to include `PR-ID` and `SCHEMA MUTATION: NO`;
- exact head `817e93dd3cfd53961f0b0ab86221182665f56b0b` passed both `W003 Governance Gate` and `qps-canonicalization`;
- PR #717 merged at `92f80b5027108a14a26c22f32c70d13b587dc853`;
- the control exception creates **zero engineering credit and zero BD state movement**.

## 16. v1.6.11 current delta — U1.5 / OFFER-21 formal supplier-return closure route

This section changes the execution route, not the engineering evidence state.

New evidence ledger: `bd005_u15_negotiation_closure_route_v1_6.yaml`.

Canonical negotiation item `QPS-GLOBAL-AGENDA-U1-5 / OFFER-21 — LOOP recovery concept` is now bound as the formal closure route for the missing quantitative LOOP chain. The current negotiation SSOT classifies it as `OPEN_ACTION / REVIEW_REQUIRED` with **closure credit 0**.

The required written updated-offer return explicitly asks for:

- initial plant state;
- helium inventory requiring recovery;
- expected peak recovery flow;
- duration of recovery;
- available approximately 110 g/s capacity;
- required cooling-water flow;
- instrument-air requirement;
- electrical/emergency-power requirement;
- storage capacity;
- consequence if a required utility is unavailable;
- resulting preserved plant state.

The same canonical row requires a source-bound return to be dispositioned and pass the exact obligation-specific re-entry test. No source-bound bidder return or BAFO evidence location is currently bound.

### Execution consequence

The prior v1.6.10 first-red of repeatedly hunting or deriving an exact ~110 g/s / <=350 kW point is replaced by a stronger first-red:

**receive and disposition the U1.5 / OFFER-21 source-bound supplier return.**

The 112 g/s / 357 kW maximum point remains valid equipment context, but interpolation from it cannot close U1.5 or BD-005. Route binding is not evidence receipt and therefore grants zero engineering closure credit.

### Current BD-005 state at v1.6.11

`U1_5_FORMAL_RETURN_ROUTE_BOUND_SUPPLIER_EVIDENCE_OPEN`

First-red sequence:

1. receive and bind the U1.5 written updated-offer return by exact source identity/version/hash;
2. disposition `ACCEPT / REJECT / DEFER` against the obligation-specific re-entry test;
3. if accepted/partial, bind the supplier-supported LOOP Hz/flow/package-power point and total EPS margin;
4. bind Recovery Cooling Water/PAB12 degraded hydraulics and ES02 critical auxiliary split;
5. bind remaining duct and thermal-model inputs;
6. execute the first-law WCS LOOP transient only after accepted electrical/hydraulic/thermal evidence is complete enough for the model.

Non-compensating rule: `INTERPOLATION != SUPPLIER EVIDENCE`, `ROUTE BINDING != EVIDENCE RECEIPT`, and negotiation source coverage/silence does not equal confirmed compliance.

BD-006 remains `PARTIAL_EVIDENCE_BOUND`; BD-008 remains `PREPARED_P0_GATED`; global/project DoV remains `WITHHELD`.