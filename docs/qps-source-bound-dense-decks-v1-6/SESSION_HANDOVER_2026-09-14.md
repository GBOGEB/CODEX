# QPS Visual Knowledge System — Lossless Session Handover

Date: 2026-09-14
Repository: `GBOGEB/CODEX`
Scope: QPS v1.6 source-bound Utilities / Controls / Naming / LOOP / graph lineage
Authority: `ENGINEERING_CURATION_NOT_DESIGN_APPROVAL`
Global/project DoV: `WITHHELD`

## 1. Session result

This session moved QPS v1.6 from source-identity uncertainty to a controlled source/content lineage with explicit engineering first-reds.

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

The Library native candidate `D2_1_CRYOGENIC_SYSTEM_CONCEPTUAL_NATIVE.docx` is not declared to be the user's sanitized derivative because one ALaT reference remains in its references section. The sanitized derivative shall be bound as a distinct file/version identity when surfaced.

### D2.2

D2.2 is the **technical and project requirements anchor**. It carries technical constraints, project requirements, interface/test requirements and project boundary conditions. It does not replace D2.1 process behavior.

## 3. D2.1 behavioral lineage recovered

D2.1 Appendix 8.2 / 8.3 / 8.4 are now treated as three separate evidence lanes:

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

## 4. BD queue at session close

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

## 5. First-red and TODO

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

## 6. 3PR receipt

The session 3PR control pass is:

### P1 — Recover

Recovered and re-read current source identity, current `main` TRIAGE, v1.5 graph carrier, D2.1 native conceptual-design text, Appendix 8.4 mode pages, and source-vs-curated lineage.

### P2 — Reconcile / prove

Reconciled:

- D2.1 process-concept role vs D2.2 requirement role;
- aged source status vs retained provenance authority;
- WCS-room LOOP transient vs Line-S cryogenic-return transient;
- v1.5 graph carrier vs richer v1.6 semantic overlay;
- sanitized derivative identity vs unsanitized/native source candidate.

No engineering acceptance was promoted by semantic reconciliation.

### P3 — Re-enter

Re-entry is accepted only at the source/lineage layer:

- D2.1 behavioral lineage may enter the graph overlay now;
- BD-008 is `PREPARED_P0_GATED`, not CLOSED;
- engineering-dependent edges remain gated by BD-005/006;
- global/project DoV remains WITHHELD.

## 7. MIP receipt

### Modernize

- repaired stale source-role language;
- separated temporal age from source authority;
- separated process-concept behavior from project requirements;
- reused the existing graph carrier instead of creating a second graph architecture;
- preserved the #700 state-reconciliation precedent that later merge time alone cannot reopen stronger retained evidence.

### Innovate

- introduced a behavioral-edge evidence lane from D2.1 Appendix 8.4;
- represented valve fallback, path availability and process state as graph-edge semantics while projecting onto existing `tree/interface/control` carrier types;
- separated WCS-room thermal survival from Line-S cryogenic return behavior so each can mature independently.

### Perpetuate

- source/provenance and engineering-acceptance states remain explicitly separate;
- OPEN edges remain OPEN in graph publication;
- the sanitized D2.1 derivative requires its own exact file/version identity;
- deterministic rendering remains deferred until graph/engineering stability;
- governed publication continues through #690/#691 rather than a QPS-specific duplicate exporter.

## 8. Non-compensating controls

- `RENDER != SOURCE AUTHORITY`
- `VISUAL PASS != ENGINEERING PASS`
- `DOCUMENT POLISH != ACCEPTANCE CREDIT`
- source/content DoV does not validate open engineering claims;
- source age is not source invalidity;
- green/color semantics require per-drawing legend/state binding;
- process fallback semantics do not automatically assign SIL or HARD_TRIP;
- candidate I/O remains candidate until L2/detail design;
- global/project DoV remains `WITHHELD`.

## 9. Restart victory condition

The next high-value victory is not another deck or renderer. It is one of:

- obtain enough BD-005 degraded-state inputs to execute the first defensible WCS-room first-law transient; or
- obtain discipline cause/effect evidence that closes one real BD-006 classification conflict.

In parallel, Appendix 8.4 valve/mode extraction may proceed as source/lineage work, but it cannot bypass those P0 engineering gates.
