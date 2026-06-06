# Federation Reconciliation Matrix

## Federation Impact Summary

PR-000 governance bootstrap artifacts are useful as review-facing entry points, but they currently duplicate existing repository authority. The highest-value path is to reuse existing CODEX/ABACUS governance and manifest architecture while turning new `docs/` directories into portal bridges or indexes.

## Artifact Classification

| Artifact | Existing Equivalent | CODEX Impact | ABACUS Impact | ARTSTYLE Impact | QPLANT Impact | Action |
|---|---|---|---|---|---|---|
| `.github/PULL_REQUEST_TEMPLATE.md` | `.github/pull_request_template.md`, `GOVERNANCE.md` review evidence model | Adds checklist; needs alignment with existing semantic wave template. | Can require validation evidence for automation outputs. | Can capture render/style scope if extended. | Can capture domain requirement evidence if linked to RTM. | BRIDGE |
| `.github/CODEOWNERS` | `DELTA_1/operational_ownership_matrix.md` | Adds GitHub review routing. | Should reflect CODEX policy / ABACUS execution split. | No direct owner mapping yet. | No direct owner mapping yet. | BRIDGE |
| `SECURITY.md` | `DELTA_1/sdlc_compliance_matrix.md`, advisory `security-scan.yml` | Adds disclosure guidance. | Should reference ABACUS DevSecOps execution responsibility. | No direct impact. | Protects project-facing reports. | KEEP |
| `CONTRIBUTING.md` | `GOVERNANCE.md`, `DELTA_1/branch_protection_manifest.md` | Adds contributor onboarding. | Should reference execution/CI responsibilities. | Can support style PR standards. | Can support domain documentation contributions. | KEEP |
| `docs/ADR/` | `06_arch/ADR/`, `DELTA_1/governance_adr_template.md` | Duplicates ADR registry unless bridged. | May need execution-decision references. | Can reference style/render ADRs. | Can reference domain/project ADRs. | BRIDGE |
| `docs/RTM/` | `docs/rtm/`, `01_requirements/RTM.csv` | Duplicate namespace by case; schema incomplete. | Existing incubator→ABACUS bridge lives in `docs/rtm/`. | No direct mapping yet. | Strong domain requirement relevance. | MERGE |
| `docs/GOVERNANCE/` | `GOVERNANCE.md`, `DELTA_1/`, `KEB/governance/`, `MANIFEST/` | Duplicates governance root if treated as authority. | Must reference CODEX/ABACUS split. | Could expose style governance references. | Could expose project governance references. | REFERENCE |
| `docs/DMAIC/` | `99_handover/PROCESS_DMAIC.md`, `maps/dmaic_phase_map.yml` | Generic lifecycle duplicate. | Existing bridge requires ABACUS phase schema validation. | Can support design/style improvement loops. | Strong quality/process relevance. | BRIDGE |

## Federation Recommendations

| Federation participant | Recommendation |
|---|---|
| CODEX | Keep CODEX as the governance, SDLC, release evidence, and federation integration authority. New docs should point back to `GOVERNANCE.md`, `DELTA_1/`, `KEB/governance/`, and `MANIFEST/`. |
| ABACUS | Preserve ABACUS as automation/execution runtime. PR-000 should not redefine ABACUS ownership; it should reference existing CODEX policy / ABACUS execution matrices. |
| ARTSTYLE | Treat ARTSTYLE as a future style/render governance consumer. Do not introduce ARTSTYLE-specific authority until a concrete style/render ADR or RTM entry exists. |
| QPLANT | Treat QPLANT as a domain-facing consumer of requirements, ADR, and DMAIC evidence. Keep QPLANT traceability anchored to canonical RTM and handover process artifacts. |

## Metrics

| Metric | Score |
|---|---:|
| governance_overlap_pct | 76 |
| rtm_overlap_pct | 72 |
| adr_overlap_pct | 68 |
| dmaic_overlap_pct | 74 |
| federation_reuse_score | 78 |

## Interpretation

A `federation_reuse_score` of **78** means PR-000 can be salvaged with high reuse if its new artifacts are repositioned as bridges, indexes, and contributor-facing entry points. Without reconciliation, PR-000 trends toward duplicate governance structure creation.
