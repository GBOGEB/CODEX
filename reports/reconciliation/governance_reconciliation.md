# Governance Reconciliation Review

## Scope

| Category | Path |
|---|---|
| New PR-000 artifact | `docs/GOVERNANCE/` |
| Existing operating model | `GOVERNANCE.md` |
| Existing governance baseline | `DELTA_1/` |
| Existing machine-readable governance | `KEB/governance/` |
| Existing manifest governance | `MANIFEST/` |

## Finding

PR-000 currently creates a duplicate governance documentation root. The existing governance architecture is already substantial: `GOVERNANCE.md` defines CODEX as a governed federation-runtime repository, `DELTA_1/` defines CODEX governance responsibilities and ABACUS execution linkage, `KEB/governance/` carries rules/metrics/glossary data, and `MANIFEST/` carries render, lineage, program metrics, and federation manifests.

## Authority Review

| Existing source | Authority already established | PR-000 interaction |
|---|---|---|
| `GOVERNANCE.md` | Repository identity, CI truth gate, Pages portal, DMAIC ledger, federation bridge model. | `docs/GOVERNANCE/` restates lightweight principles without referencing the operating model. |
| `DELTA_1/` | Governance baseline, SDLC controls, ownership, release, branch, audit, and runtime support. | New charter/controls overlap but are much thinner. |
| `KEB/governance/` | Machine-readable governance rules, metrics, glossary. | New docs do not connect controls to existing data contracts. |
| `MANIFEST/` | ABACUS render pipeline, federation glossary, lineage, program metrics, roadmaps. | New docs do not register with manifest/federation lineage. |

## Conflicting Authorities

1. `docs/GOVERNANCE/controls.md` defines `GOV-001` through `GOV-004`, but existing `DELTA_1/` already defines governance controls and matrices.
2. `docs/GOVERNANCE/charter.md` defines generic roles, while `DELTA_1/operational_ownership_matrix.md` already splits CODEX and ABACUS ownership.
3. `docs/GOVERNANCE/README.md` presents `docs/GOVERNANCE/` as the governance home, but `GOVERNANCE.md` is the current top-level operating model.

## Federation Relevance

The new governance artifacts have governance value, but they do not yet encode the federation architecture. Missing links include:

- CODEX as the governance and integration repository.
- ABACUS as execution runtime / CI/CD / DevSecOps / deployment automation.
- ARTSTYLE as a presentation/style federation participant when applicable.
- QPLANT as a domain/project-facing consumer of governed outputs.
- Bridge/federation outputs under `reports/bridge/*` and `reports/federation/*` described in `GOVERNANCE.md`.

## Metrics

- `governance_overlap_pct`: **76**
- Lexical new-term coverage against existing governance corpus: **56.3%**
- Authority overlap: **high**, because PR-000 introduces controls, roles, and governance-home language without referencing existing authorities.

## Recommendation

Classify `docs/GOVERNANCE/` as **REFERENCE**. It should become a public-facing index that references `GOVERNANCE.md`, `DELTA_1/`, `KEB/governance/`, and `MANIFEST/`, rather than a new policy authority.
