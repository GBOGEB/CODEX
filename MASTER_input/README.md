# MASTER Contract Workbench SSOT

`MASTER_input/` is the authoritative YAML-first Single Source of Truth (SSOT) for the MASTER Contract Workbench. Generated Excel workbooks, HTML workbenches, reports, dashboards and snapshots are derivative artefacts only; they must never become the System of Record.

## Ownership model

| Owner | Responsibility |
| --- | --- |
| ABACUS | Contract data, governance, traceability and lifecycle state |
| CODEX | Automation, generation, validation and CI/CD |
| ARTSTYLE | Visualization, dashboards and user experience |

## Directory map

| Path | Purpose |
| --- | --- |
| `schemas/contract_schema.yaml` | YAML 1.2 SSOT schema and governance constraints |
| `contracts/master-contract/contract.yaml` | Baseline MASTER contract SSOT instance |
| `change_requests/` | Approved change requests that bridge derivative edits back to YAML |
| `checkpoints/` | Runtime lifecycle snapshots emitted from the SSOT; payloads are generated on demand and ignored by git |
| `generated/excel/` | Generated workbook outputs; payloads are not committed |
| `generated/html/` | Generated human workbench outputs; payloads are not committed |
| `generated/reports/` | Generated audit/traceability reports; payloads are not committed |
| `generated/dashboards/` | Generated dashboard-ready JSON/HTML outputs; payloads are not committed |

## Governance rule

If it cannot be traced, it cannot be governed. If it cannot be governed, it cannot be contracted. If it cannot be contracted, it cannot be executed.


## Drift guard

Run `python scripts/check_contract_workbench.py` before opening changes. The check validates the YAML SSOT, rejects tracked derivative payloads, regenerates derivatives twice in temporary workspaces, compares portable manifests plus SHA-256 output hashes, and fails if existing generated workspace payloads differ from regenerated hashes. When existing generated payloads are present, the guard reuses `generated_at` from the existing generated manifest so timestamp differences do not create false drift failures. It does not compare against committed generated artefacts because those artefacts are intentionally not committed. Runtime checkpoints are generated on demand; CI temporary workspaces are automatically deleted, but cleanup of user-invoked runtime outputs is a documented policy responsibility rather than an automated repository guarantee. Formal retention decisions belong to ABACUS per `generation_policy.yaml`.


## Review verification matrix

| Reviewer concern | Repository control |
| --- | --- |
| Drift guard scope | `scripts/check_contract_workbench.py` regenerates derivatives twice in temporary workspaces, compares the complete portable manifests including SHA-256 hashes, reuses existing manifest timestamps for workspace comparisons, and fails when existing generated payload hashes drift. |
| Tracked generated payloads | The guard scans tracked files under `MASTER_input/generated/` and `MASTER_input/checkpoints/`; only `.gitignore` and `.gitkeep` placeholders are allowed. |
| CI trigger paths | `.github/workflows/contract-workbench.yml` runs on changes to `MASTER_input/**`, `src/contract_workbench/**`, the generator/check scripts and the focused tests. |
| Checkpoint retention | CI temporary workspaces are deleted automatically; user-invoked runtime output cleanup is policy-only, and formal archive/retention belongs to ABACUS. |
| Negative-test isolation | Contract governance tests assert specific validation messages for each violation class. |
