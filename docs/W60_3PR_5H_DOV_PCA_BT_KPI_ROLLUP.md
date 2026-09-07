# W60 3PR 5-Horizon DoV/PCA/BT/KPI Roll-up

Repository: `GBOGEB/CODEX`
Plane: KEB governance semantics
Date: 2026-09-07

## Session vs Global DoV

Session/chat DoV is limited to this branch: KEB controls can describe the semantic receipt, policy boundaries, and payload-SHA gate. Global DoV remains pending until QPS supplies the accepted SSOT payload SHA and ABACUS supplies the matching runtime receipt.

## Five Horizons

| Horizon | Scope | Evidence needed | Current state |
|---|---|---|---|
| H0 session/chat | This branch | Control packet and schema extension | Defined |
| H1 next pulse | P1-P3 | Real KEB receipt for the identical QPS payload SHA | Pending |
| H5 five-wave | P4-P6 | Policy/provenance receipts for accepted regenerated artifacts | Blocked by P3 |
| H50 portfolio | Cross-repo convergence | One receipt contract family and low duplication | Deferred |
| H100 sustained | Governed semantic autonomy | Stable policy versioning and reproducible receipts | Deferred |

## P1-P7 Controls

KEB owns semantic/provenance validation for P1 and P2, recommends child re-entry disposition in P3, observes artifact lineage in P4/P5, rechecks semantic zero-delta in P6, and participates in schema cleanup only after the stable baseline exists.

## PCA and Reverse-Load Priority

The low-scoring KEB dimensions are child re-entry semantics, binary lineage policy, duplicate schema governance, and exact hash governance. Reverse-load priority is highest where one missing receipt blocks multiple downstream controls.

Current highest reverse-load blocker: `child_reentry_semantics`.

## BT Priority

1. P2 real KEB receipt contract
2. P3 child re-entry recommendation path
3. P1 identical-SHA governance gate
4. P5 cross-binary policy tuple check
5. P6 zero-delta semantic recheck
6. P7 duplicate schema cleanup

## KPI Position

Session/chat DoV: `0.63`
Global DoV: `0.47`

These are planning/control estimates only. KEB semantic readiness does not replace DOW runtime QA or QPS child acceptance.
