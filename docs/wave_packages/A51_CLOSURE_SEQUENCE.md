# A51 — Sequential TODO Closure and Reusable Process Governance

## Purpose

A51 turns the remaining package TODOs into an ordered, reusable closure sequence. It documents what remains after A49/A50 and prevents the word `partial` from hiding incomplete work.

## Closure principle

Each missing capability is closed by a dedicated wave with a specific artifact, metric, validation check, and PR scope.

## Sequential closure waves

| Wave | Closure target | Core artifacts | Repo scope | Exit criterion |
|---|---|---|---|---|
| A51 | reusable process and TODO ledger | this file, closure ledger | CODEX | all TODOs named |
| A52 | KPI and metric registry | `kpi_registry.yaml`, `metric_weights.yaml` | CODEX | every KPI has definition/equation |
| A53 | DMAIC governance | `dmaic_registry.yaml`, `dmaic_process.md` | CODEX | each wave mapped to DMAIC |
| A54 | PCA and covariance registry | `pca_axes.yaml`, `covariance_registry.yaml` | CODEX/ABACUS bridge | axes and covariances defined |
| A55 | topology and lineage registry | `wave_registry.yaml`, `artifact_lineage.yaml` | CODEX | forward/back recursion mapped |
| A56 | federation bridge registry | `federation_registry.yaml` | CODEX + ABACUS | affected repos and bridge roles clear |
| A57 | runtime and visualization closure | Plotly/HTML runtime docs | CODEX | graph and table runtime specified |
| A58 | CI/rebuild closure | build and validation scripts | CODEX | package can be regenerated |
| A59 | release-candidate governance | release checklist | CODEX + ABACUS | ready-for-review package |
| A60 | final handover and hosted entry closure | handover, index, entry map | CODEX | user entry points confirmed |

## Current known remaining TODOs

| TODO | Status | Next wave |
|---|---|---|
| canonical KPI registry | open | A52 |
| metric weighting equations | open | A52 |
| DMAIC explicit mapping | open | A53 |
| PCA axes and covariance artifacts | open | A54 |
| wave registry / topology manifest | open | A55 |
| CODEX ↔ ABACUS federation registry | open | A56 |
| Plotly hydration and topology graph runtime | open | A57 |
| CI validation / rebuild automation | open | A58 |
| final PR/readiness checklist | open | A59 |
| hosted Pages entry confirmation | open | A60 |

## Reuse rule

Future iterations must update this closure ledger rather than using ambiguous language such as `partial` without listing the missing scope.
