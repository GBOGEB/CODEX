# ADR Reconciliation Review

## Scope

| Category | Path |
|---|---|
| New PR-000 artifact | `docs/ADR/` |
| Existing ADR artifact | `06_arch/ADR/` |
| Existing governance ADR pattern | `DELTA_1/governance_adr_template.md` |

## Finding

PR-000 currently creates a duplicate ADR location rather than extending the established architecture. The existing `06_arch/ADR/ADR.md` already contains an accepted ADR with the standard sections `Context`, `Decision`, `Status`, `Consequences`, `Alternatives Considered`, `Related Requirements`, `Risks & Mitigations`, and `SBS Mapping`. The new `docs/ADR/template.md` repeats the generic ADR shape but omits established domain fields such as related requirements details, risks, mitigations, and SBS mapping.

## Overlap Assessment

| Dimension | Evidence | Assessment |
|---|---|---|
| Naming | `docs/ADR/template.md` uses `ADR-000`; `06_arch/ADR/ADR.md` uses `ADR-001`. | High overlap in record identity. |
| Section model | Both use context, decision, consequences, alternatives, and status. | Duplicate template structure. |
| Requirement linkage | Existing ADR references `RTM.001–RTM.008`; new template only has `Related RTM`. | New artifact is less specific. |
| Governance template | `DELTA_1/governance_adr_template.md` already supplies a governance ADR template. | Duplicate governance pattern. |
| Repository placement | Existing ADRs live in `06_arch/ADR/`; new ADRs live in `docs/ADR/`. | Conflicting ownership unless bridged. |

## Metrics

- `adr_overlap_pct`: **68**
- Lexical new-term coverage against existing ADR/governance ADR corpus: **34.9%**
- Structural overlap: **high**, because the same ADR lifecycle and core sections are repeated.

## Duplicate Templates

- `docs/ADR/template.md` duplicates the generic decision-record intent of `DELTA_1/governance_adr_template.md`.
- `docs/ADR/README.md` introduces a lifecycle taxonomy already implied by existing ADR status usage and the DELTA_1 governance ADR template.

## Missing References

PR-000 ADR artifacts should reference:

1. `06_arch/ADR/ADR.md` as the current architectural ADR root.
2. `DELTA_1/governance_adr_template.md` as the governance ADR template source.
3. `01_requirements/RTM.csv` as the current requirements linkage source.
4. `99_handover/PROCESS_DMAIC.md` for the existing DMAIC evidence loop.

## Recommended Ownership

| Path | Recommended owner role | Rationale |
|---|---|---|
| `06_arch/ADR/` | Architecture owner | Existing technical ADR source of truth. |
| `DELTA_1/governance_adr_template.md` | Governance owner | Existing governance decision template. |
| `docs/ADR/` | Documentation bridge owner | Should be a portal/index that references canonical ADR sources, not a new ADR system of record. |

## Recommendation

Classify `docs/ADR/` as **BRIDGE**. Keep it only if it becomes a human-facing index and template pointer to `06_arch/ADR/` and `DELTA_1/governance_adr_template.md`. Do not treat `docs/ADR/` as a parallel ADR registry.
