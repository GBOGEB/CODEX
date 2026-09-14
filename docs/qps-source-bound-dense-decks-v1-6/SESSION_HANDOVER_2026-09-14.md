# QPS Visual Knowledge System — Lossless Session Handover

Date: 2026-09-14
Current control version: `v1.6.9`
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

### Current contractual refinement

`SCK CEN/90508872` Addendum II is treated as the current contractual tender-requirements surface where its requirements apply. It refines the current contractual boundary without erasing D2.1 or D2.2 provenance.

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

The pulse added `d2_1_mode_state_matrix_v1_6.yaml` and advanced BD-008 source extraction without granting engineering credit.

Source-bound mode families include cool-down, warm-up, purge/fill, distribution vacuum loss, single-QM vacuum loss, minor QCELL fault, quench proposal, loss of utility and cryoplant trip.

Named valve behavior source-bound at text level includes:

- `CV503`: controls bottom helium supply used for cavity gas circulation during cool-down;
- `HV510` / `HV520`: local manual purge/fill hand valves;
- minor QCELL fault: supply `NC` / return `NO` process fallback semantics;
- loss of utility / cryoplant trip: `NO` paths open and `NC` paths close according to the conceptual fallback description.

This is a **source mode/state matrix**, not a final cause/effect matrix. Exact Appendix 8.4 diagram-to-mode mapping, visible valve-state extraction and colour-legend decoding remain open.

## 5. v1.6.9 bounded pulse — contractual LOOP boundary sharpened

`bd005_addendum_loop_boundary_v1_6.yaml` now binds the authoritative Addendum II degraded-utility requirements and separates them from bidder, derivative and working-slide statements.

### Contractual LOOP boundary

- **RTM-401:** up to 350 kW backup diesel power is available after an interruption of a few minutes. This does not allocate the full 350 kW to one HP compressor.
- **RTM-428:** up to 350 kW backup cooling-water capacity is available after a few minutes; the backup header is hydraulically common with the normal WCS header and may operate at reduced total flow.
- **RTM-432 / RTM-433:** no continuous normal instrument air is available during LOOP beyond initial valve actuations; QPS must provide pneumatic backup for helium recovery with **6 h autonomy under full recovery load**.
- **RTM-434 / RTM-435:** dedicated exhaust ducts connect to each HP compressor; steady-state WCS heat to room air is capped at 120 kW and at least 50% shall be transferred directly to the exhaust ducts.
- **RTM-436:** during LOOP the HP exhaust ducts remain available without restriction and **no more than 15 kW may be dissipated to the compressor-room ambient air**.
- **RTM-258 / 260 / 261 / 262:** limited services shall support LOOP helium recovery; abnormal QRB.S return capability is at least 100 g/s; recovery to normal circulation is required.

### Semantic corrections

- The source **6 h pneumatic autonomy** requirement is not proof of the separate working `~6 h` WCS-room thermal-stabilization statement.
- The historical `~17 kW` heat path remains useful provenance, but the current contractual LOOP ambient-room heat ceiling is **≤15 kW**.
- The current bidder `~110 g/s` one-emergency-compressor claim remains `REVIEW_REQUIRED`; it is not the contractual acceptance point.
- The current analytical `72 Hz / ~112 g/s / ~357 kW` point remains an equipment maximum reference; it shall not be linearly scaled into the LOOP operating point.
- The derivative `Support System ICD & Requirements Update` is retained as a navigation clue only where its RTM numbering diverges from Addendum II. Addendum II numbering/content controls the contractual crosswalk.

### What this closes vs does not close

This pulse closes the *contractual boundary subquestions* for backup power, backup-PCW thermal capacity/topology, pneumatic autonomy, LOOP room ambient-heat ceiling, HP exhaust-duct availability and minimum abnormal QRB.S return flow.

It does **not** close BD-005. The executable first-law transient still needs the selected OEM/contractor operating point, actual degraded hydraulic state, duct-flow data, thermal mass and temporal criteria.

## 6. BD queue at current close

| ID | Priority | State | Current meaning |
|---|---|---|---|
| BD-001 | P0 | CLOSED | exact source bytes bound |
| BD-002 | P0 | CLOSED | 63 source renders bound |
| native-text binding | P0 | CLOSED | native text bound to same slide identities |
| BD-003 | P0 | CLOSED_CONTENT_TRACE_DOV | 63/63 reviewed, zero silent drop; five lineage repairs |
| BD-004 | P0 | CLOSED_SCOPE_RECONCILED | utilities value scopes reconciled only |
| **BD-005** | **P0** | **CONTRACTUAL_LOOP_BOUNDARY_SHARPENED / OPEN** | contractual degraded limits now bound; selected equipment/hydraulic/thermal transient inputs remain open |
| **BD-006** | **P0** | **PARTIAL_EVIDENCE_BOUND** | process fallback + tender classification bound; discipline cause/effect open |
| BD-007 | P1 | OPEN_L2_GATED | detailed I/O awaits L2/detail design |
| BD-008 | P1 | PREPARED_P0_GATED | source mode/state matrix bound; diagram/colour visual binding + P0 engineering edges remain open |
| BD-009 | P1 | DEFER_TO_V1_7 | deterministic render after engineering/graph stabilization |
| BD-010 | P1 | REFRAME_BIND_EXISTING_CARRIER | reuse merged #690/#691 publication carrier |

## 7. First-red and TODO

### P0 — BD-005 LOOP / degraded state

The first-red is now narrower. Obtain and bind:

1. current OEM/contractor HP operating point for the selected `~110 g/s` emergency-recovery state, including frequency, electrical input and cooling-water rejection;
2. ES02 auxiliary split and demonstrated margin within the contractual up-to-350-kW backup-power boundary;
3. actual PAB12 LOOP flow, pressure, supply/return temperatures, pump/fan power and valve state within the RTM-428 reduced-flow common-header boundary;
4. OFFER-35 duct interface size, flow rate and allowable pressure drop for the selected HP package;
5. quantitative HV03 degraded/LOOP room airflow or proof that the RTM-436 duct path plus ≤15 kW ambient ceiling is sufficient for the selected model boundary;
6. effective free room volume and equipment/building thermal mass;
7. physical variable and limit behind the working `~2 h` onset statement;
8. measurable thermal stabilization criterion behind the working `~6 h` statement, kept separate from RTM-433 pneumatic autonomy;
9. first-law WCS LOOP transient with uncertainty and independent review.

D2.1 Line-S transient evidence remains a separate lane and shall not substitute for the WCS-room thermal model.

### P0 — BD-006 Controls

Only close classifications when discipline evidence proves cause/effect, fail-safe/loss-of-signal behavior, exact protocol/owner boundary, trip/permissive consequence and relevant L2 I/O allocation. D2.1 fallback behavior and utility/LOOP requirements do not automatically create a hard trip.

### P1 — BD-008 graph

Use the existing v1.5 graph carrier. The source/lineage overlay is strengthened by the mode/state matrix. Next graph work remains: diagram/page → mode mapping; exact valve-state extraction; per-diagram colour/legend binding; contradiction checking; keep BD-005/006 engineering edges visibly OPEN.

## 8. 3PR receipt

### P1 — Recover

Recovered current `main`, negotiation/compliance evidence, current analytical SSOT, Addendum II contractual requirements, Drive derivative surfaces and existing D2.1/D2.2 lineage.

### P2 — Reconcile / prove

Reconciled D2.1 process role, D2.2 requirements role, current Addendum contractual refinement, bidder ~110 g/s claim, equipment-maximum ~112 g/s/~357 kW analytical guard, derivative ICD crosswalk, six-hour pneumatic autonomy and separate thermal-stabilization wording.

### P3 — Re-enter

Addendum II degraded-utility boundaries may enter BD-005 as contractual model constraints. Executable transient/engineering acceptance remains deferred.

## 9. MIP receipt

### Modernize

- corrected derivative RTM crosswalk against authoritative Addendum II;
- separated pneumatic six-hour autonomy from thermal-stabilization wording;
- replaced vague LOOP room-heat assumptions with explicit contractual ≤15 kW ambient ceiling while retaining historical provenance.

### Innovate

- converted limited-utility requirements into a typed degraded-state model boundary without fabricating missing hydraulic, airflow or thermal-mass inputs;
- separated contractual ceilings from selected-equipment operating-point evidence.

### Perpetuate

- source/provenance and engineering-acceptance states remain explicitly separate;
- same canonical TRIAGE/full-handover/drop-in outputs remain synchronized;
- `SESSION_PROGRESS_LEDGER_2026-09-14.yaml` records this as `TUPLE-005`;
- additive evidence stays in dedicated ledgers.

## 10. Lossless reproduction contract

The same three canonical outputs remain the current-state surfaces:

1. `triage_v1_6.yaml`
2. `SESSION_HANDOVER_2026-09-14.md`
3. `DROP_IN_CONTINUATION_2026-09-14.md`

The append-only progression surface is:

4. `SESSION_PROGRESS_LEDGER_2026-09-14.yaml`

Additive engineering/source evidence remains in dedicated ledgers; do **not** fork the handover architecture.

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
→ refresh TRIAGE + full handover + drop-in in same PR
→ verify canonicalization/governance gates
→ merge
→ post-merge read from main
```

## 11. Major prompt/reply tuple progression contract

A tuple is **major** when it changes evidence/source lineage, BD state/priority/close predicate, source authority/currentness interpretation, first-red/execution sequence, graph/behavior semantics, the handover contract, or material PR/merge context needed for restart.

After each major tuple:

- append one progression-ledger entry capturing user intent, executed delta, repository receipt, BD movement/non-movement and DoV/credit boundary;
- refresh the same three canonical current-state outputs in the same bounded PR;
- preserve additive engineering/source ledgers separately;
- verify governance/canonicalization gates where applicable;
- post-merge read from `main`.

Minor no-state-change turns may be folded into the next major tuple. Historical tuple summaries never override stronger current TRIAGE/evidence.

## 12. Non-compensating controls

- `RENDER != SOURCE AUTHORITY`
- `VISUAL PASS != ENGINEERING PASS`
- `DOCUMENT POLISH != ACCEPTANCE CREDIT`
- source/content DoV does not validate open engineering claims;
- derivative requirement tables cannot override authoritative Addendum requirements;
- 350 kW backup power is a boundary, not proof of one-compressor allocation;
- 350 kW backup PCW is thermal capacity, not a proven emergency flow;
- 6 h pneumatic autonomy is not a 6 h thermal-transient validation;
- 15 kW LOOP ambient heat is a source ceiling, not a complete room thermal model;
- duct availability is not quantitative HV03 airflow;
- process fallback semantics do not automatically assign SIL or HARD_TRIP;
- candidate I/O remains candidate until L2/detail design;
- global/project DoV remains `WITHHELD`.

## 13. Restart victory condition

The next high-value victory is now:

- bind the **current selected ~110 g/s HP operating point + ES02 margin + PAB12 degraded hydraulic state + OFFER-35 duct data**, then execute the first defensible WCS-room first-law transient;

or, independently:

- obtain discipline cause/effect evidence that closes one real BD-006 classification conflict.

In parallel, Appendix 8.4 diagram/valve/colour extraction may continue as source/lineage work, but it cannot bypass the P0 engineering gates.
