# RTM Reconciliation Review

## Scope

| Category | Path |
|---|---|
| New PR-000 artifact | `docs/RTM/` |
| Existing runtime RTM docs | `docs/rtm/` |
| Existing requirement table | `01_requirements/RTM.csv` |
| Existing requirement JSON | `01_requirements/requirements.json` |

## Finding

PR-000 creates a second RTM documentation namespace with different casing: `docs/RTM/` versus existing `docs/rtm/`. The existing RTM sources already include CSV requirement rows and runtime/federation lineage bridge documents. The new `docs/RTM/template.md` is conceptually compatible but does not preserve the current CSV schema.

## Existing Schema

`01_requirements/RTM.csv` uses this header:

```text
ReqID,Shall Statement,Class,Verification,Deliverables,Source Reference
```

Existing `docs/rtm/local_rtm_lineage.md` uses this bridge-oriented lineage table:

```text
Unique ID | Parent Requirement | Proto-Need | Implementation Path | Verification Method | Status
```

New `docs/RTM/template.md` uses this metadata table:

```text
Requirement ID | Title | Source | Owner | Status | Evidence | Related ADR | Related DMAIC Phase | Notes
```

## Overlap Assessment

| Dimension | Evidence | Assessment |
|---|---|---|
| Namespace | `docs/RTM/` and `docs/rtm/` differ only by case. | High duplication risk. |
| Identifier | `Requirement ID` maps to `ReqID` / `Unique ID`. | Compatible with mapping. |
| Source | New `Source` maps to `Source Reference`. | Partially compatible. |
| Verification | Existing schema has `Verification`; new template uses `Evidence`. | Needs normalization. |
| Deliverables | Existing CSV has `Deliverables`; new template has no direct field. | Missing field. |
| Class | Existing CSV has `Class`; new template has no direct field. | Missing field. |
| Federation lineage | Existing `docs/rtm/` covers ABACUS/federation bridge context. | New artifact omits federation bridge details. |

## Metrics

- `rtm_overlap_pct`: **72**
- Lexical new-term coverage against existing RTM corpus: **38.3%**
- Schema compatibility: **partial**; identifiers, source, status, and evidence can map, but `Class`, `Verification`, and `Deliverables` need explicit fields.

## Migration Strategy

1. Treat `01_requirements/RTM.csv` as the canonical requirements table until a formal schema migration is approved.
2. Treat `docs/rtm/` as the canonical runtime/federation RTM documentation namespace.
3. Convert `docs/RTM/` into a bridge/index or merge it into `docs/rtm/` to avoid casing ambiguity.
4. If the new metadata template is retained, add compatibility fields for `Class`, `Verification`, `Deliverables`, and `Source Reference`.
5. Define a one-way import/export mapping before changing any requirement IDs.

## Recommendation

Classify `docs/RTM/` as **MERGE** into `docs/rtm/`. The uppercase namespace should not remain as an independent RTM root.
