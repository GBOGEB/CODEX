# PR-000A Governance Bootstrap Reconciliation Matrix

PR-000A converts the PR-000 bootstrap documentation areas into bridge, merge, and reference layers. Canonical ownership remains with the existing repository sources listed below.

| New Artifact    | Canonical Source | Action    |
| --------------- | ---------------- | --------- |
| docs/ADR        | 06_arch/ADR      | BRIDGE    |
| docs/RTM        | docs/rtm         | MERGE     |
| docs/GOVERNANCE | GOVERNANCE.md    | REFERENCE |
| docs/DMAIC      | PROCESS_DMAIC.md | BRIDGE    |

## Reconciliation notes

- `docs/ADR/` is limited to navigation, onboarding, and reference guidance for canonical ADR material in `06_arch/ADR/` and the governance ADR template in `DELTA_1/governance_adr_template.md`.
- `docs/RTM/` is limited to merge/reference guidance for canonical RTM material in `docs/rtm/` and `01_requirements/RTM.csv`.
- `docs/GOVERNANCE/` is limited to federation indexing and navigation across `GOVERNANCE.md`, `DELTA_1/`, `KEB/governance/`, and `MANIFEST/`.
- `docs/DMAIC/` is limited to quick-start, navigation, and federation bridge guidance for the canonical DMAIC process in `99_handover/PROCESS_DMAIC.md`.

## Non-authoritative guardrail

These PR-000A bridge directories must not introduce duplicate templates, parallel RTM schemas, alternate governance authority, or forked DMAIC lifecycle definitions.
