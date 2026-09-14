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

### Current BD-005 state

`CONTRACTUAL_LOOP_BOUNDARY_SHARPENED_EXECUTABLE_TRANSIENT_INPUTS_OPEN`

Newly closed subquestions are contractual backup-power ceiling/delay, backup-PCW thermal ceiling/common-header degraded-flow allowance, pneumatic-autonomy scope, LOOP ambient-room heat ceiling, HP exhaust-duct availability, and contractual abnormal QRB.S minimum flow.

### Current first-red after v1.6.9

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
