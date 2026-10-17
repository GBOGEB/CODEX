# MissionControl federation / Mycelium / MASTER_DAGS crosswalk — W1

This W1 bridge is **additive, review-only**; no new orchestration authority or remote mutation.

## Existing CODEX infrastructure reused

- Canonical Mycelium control: `mission_control/mycelium/control_manifest.yaml`.
- Its executable projection: `mission_control/mycelium/executable_projection.json`.
- Native typed-graph semantics: `mission_control/mycelium/continuity/mycelium_continuity/graph.py`, especially `validate_graph` and `schedule_sipoc`.
- Native authenticated-byte qualification boundary: `mission_control/mycelium/continuity/mycelium_continuity/native_bridge.py`.
- CODEX transport: `scripts/missioncontrol_authenticated_transport.py` (stage only).
- New review-level graph: `docs/data/missioncontrol_federated_dag_v1.json`.
- New adapter: `scripts/missioncontrol_federated_crosswalk.py`.

`MASTER_DAGS` exact canonical source is **UNKNOWN** at W1: neither a canonical repository path nor exact-source acceptance receipt has been verified. The adapter intentionally exports `master_dags_canonical_path: null` and an explicit unresolved status. Do not infer that a same-named dashboard, graph or proposal is the MASTER_DAGS SSOT.

## Semantics

The universal graph may include reference/feedback cycles. Only `dependency` edges become `SIPOC_DEPENDENCY`; the resulting executable portion must be acyclic. Nodes and edges remain `DECLARED`, never `RECEIPT_BOUND` or `ACCEPTED`, until independent GitHub run/job/attempt, ZIP digest and source-head verification through existing Mycelium routines. Links to CODEX, ABACUS, QPS and cryoplant do not grant dispatch capability.

## Build and verify

```bash
python -m pytest tests/test_missioncontrol_federated_crosswalk.py -q
python -m scripts.missioncontrol_federated_crosswalk
```

Expected review-only structural counts at W1: 18 nodes, 20 typed edges, 12 declared SIPOC dependencies; an existing Mycelium graph validator must accept the crosswalk. This is not the total all-repo census.

## Admission hold

ABACUS #1860 P0 HOLD; CODEX #977 executor promotion withheld. Current main and PR coverage, causal BD root closure, accepted CODEX-to-ABACUS REX and first correctly admitted main SHA remain UNKNOWN. No security waiver or authority transfer.
