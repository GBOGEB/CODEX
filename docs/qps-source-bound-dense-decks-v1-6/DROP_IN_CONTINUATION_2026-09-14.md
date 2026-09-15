# QPS v1.6 — Drop-in continuation

Use this block to restart without architecture rediscovery.

```text
Continue GBOGEB/CODEX QPS Visual Knowledge System from the 2026-09-14 v1.6.11 control handover.

READ FIRST:
- docs/qps-source-bound-dense-decks-v1-6/triage_v1_6.yaml
- docs/qps-source-bound-dense-decks-v1-6/SESSION_HANDOVER_2026-09-14.md
- docs/qps-source-bound-dense-decks-v1-6/DROP_IN_CONTINUATION_2026-09-14.md
- docs/qps-source-bound-dense-decks-v1-6/SESSION_PROGRESS_LEDGER_2026-09-14.yaml
- docs/qps-source-bound-dense-decks-v1-6/bd005_u15_negotiation_closure_route_v1_6.yaml
- docs/qps-source-bound-dense-decks-v1-6/bd005_current_lkt_fsd575_loop_point_v1_6.yaml
- docs/qps-source-bound-dense-decks-v1-6/bd005_addendum_loop_boundary_v1_6.yaml
- docs/qps-source-bound-dense-decks-v1-6/d2_1_behavioral_lineage_v1_6.yaml
- docs/qps-source-bound-dense-decks-v1-6/d2_1_mode_state_matrix_v1_6.yaml
- docs/qps-source-bound-dense-decks-v1-6/graph_binding_overlay_v1_6.yaml
- docs/qps-source-bound-dense-decks-v1-6/source_vs_curated_dov_v1_6.yaml
- docs/qps-source-bound-dense-decks-v1-6/state_reconciliation_v1_6.yaml

CURRENT CONTROL STATE:
- version = v1.6.11
- global/project DoV = WITHHELD
- authority = ENGINEERING_CURATION_NOT_DESIGN_APPROVAL
- BD-005 = U1_5_FORMAL_RETURN_ROUTE_BOUND_SUPPLIER_EVIDENCE_OPEN
- BD-006 = PARTIAL_EVIDENCE_BOUND
- BD-008 = PREPARED_P0_GATED

FIRST RED:
Receipt and disposition of the source-bound U1.5 / OFFER-21 written updated-offer return.

U1.5 FORMAL CLOSURE ROUTE:
- canonical item = QPS-GLOBAL-AGENDA-U1-5 / OFFER-21 LOOP recovery concept
- state = OPEN_ACTION / REVIEW_REQUIRED
- closure credit = 0
- required return = quantitative LOOP recovery basis including initial state, recovery inventory, expected peak recovery flow, duration, available ~110 g/s capacity, required cooling-water flow, instrument-air requirement, emergency electrical requirement, storage capacity, consequence of unavailable utility, and resulting preserved plant state
- current bidder return / BAFO evidence location = not source-bound
- re-entry rule = source-bound return must be dispositioned and pass the exact obligation-specific re-entry test

HARD EXECUTION RULE:
Do NOT continue trying to close the ~110 g/s / <=350 kW predicate by interpolation from the 112 g/s / 357 kW maximum point. That maximum remains useful context but is not acceptance evidence for the LOOP point. U1.5 route binding is not evidence receipt and grants zero engineering closure credit.

ON U1.5 RETURN RECEIPT:
1. bind exact source identity/version/hash and return location;
2. disposition ACCEPT / REJECT / DEFER against the exact U1.5 obligation-specific re-entry test;
3. if ACCEPT/PARTIAL, bind the supplier-supported LOOP Hz/flow/package-power point and total EPS margin;
4. bind Recovery Cooling Water/PAB12 flow, pressure, temperatures, pump/fan power and valve state;
5. bind ES02 critical auxiliary split/simultaneity and remaining duct/thermal inputs;
6. only after accepted electrical/hydraulic/thermal inputs exist, execute the first-law WCS LOOP transient with uncertainty and independent review.

RETAINED CURRENT EVIDENCE:
- selected fleet = 4 x KAESER FSD575 SFC water-cooled
- equipment maximum = 112.0 g/s at 14 bara / 72 Hz, 357 kW +/-5%
- EPS limitation = 350 kW
- two compressors connected to EPS for redundancy; only one operates during LOOP due generator size
- bidder conceptual LOOP claim = up to approximately 110 g/s with one emergency-powered compressor
- normal compressor cooling-water reference = 18.5 m3/h per compressor; it is NOT PAB12/LOOP recovery flow
- Recovery Cooling Water without glycol = TO BE DEFINED in current bidder Basis of Process Design
- cooling air = 5000 m3/h main + 4200 m3/h SFC, 40 Pa max added duct pressure drop
- heat paths at maximum point = 17.4 kW compressor cooling air + 10.7 kW SFC cooling air + 13.9 kW ambient radiation
- OFFER-35 flow and pressure-drop response is bound; duct connection size remains open

NON-COMPENSATING RULES:
- interpolation != supplier evidence
- route binding != evidence receipt
- negotiation source coverage/silence != confirmed compliance
- selected maximum point != proven LOOP operating point
- 357 kW +/-5% at 112 g/s != margin inside 350 kW EPS
- 18.5 m3/h normal CW != PAB12 LOOP flow
- 350 kW backup PCW != proven emergency flow rate
- 13.9 kW ambient heat below 15 kW ceiling != room transient closure
- six-hour pneumatic autonomy != six-hour thermal stabilization
- VISUAL PASS != ENGINEERING PASS
- DOCUMENT POLISH != ACCEPTANCE CREDIT

PARALLEL LANES:
- BD-006 only closes on discipline cause/effect, fail-safe/loss-of-signal, exact protocol/owner boundary, trip/permissive consequence and L2 allocation evidence.
- BD-008 may continue Appendix 8.4 diagram/page, valve-state and colour-legend binding, but remains P0-gated and cannot compensate for BD-005/006.

MAJOR-TUPLE CONTROL:
major prompt -> bounded execution -> evidence ledger -> progression entry -> refresh TRIAGE/full handover/drop-in -> W003 + qps-canonicalization on exact head -> merge -> post-merge read from main.

NEXT ACTION:
Do not perform another blind OEM/source interpolation hunt. Check for a new source-bound U1.5 bidder/BAFO return. If absent, preserve OPEN with zero credit. If present, bind and disposition it, then recurse on the first non-compensating evidence red.
```