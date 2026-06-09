# Federation Workspace Reference

This page documents the local workspace bootstrap contract for `GBOGEB_FEDERATION`. It is a reference layer that points to the machine-readable workspace configuration at `governance/federation_workspace.yml`.

## Workspace Contract

| Field | Value |
|---|---|
| Workspace version | `1.0` |
| Federation name | `GBOGEB_FEDERATION` |
| Python version | `3.12` |
| Virtual environment | `federation` |
| Bootstrap | enabled |
| Recovery | enabled |
| Evidence root | `EVIDENCE/` |
| Outputs root | `OUTPUTS/` |

## Federation Members

| Member | Repository branch guidance |
|---|---|
| CODEX | `develop` |
| GEMINI | `main` |
| ABACUS | `develop` |
| ARTSTYLE | Not specified in workspace repository map |
| QPLANT | Not specified in workspace repository map |

## Guardrails

- This reference does not start PR-001, SDK integration, or CI workflow work.
- Branch guidance is workspace configuration only; verify remote branch availability before checkout or push operations.
- Evidence and output directories are local roots for generated artifacts and should link back to canonical governance sources when used for audit or release evidence.
