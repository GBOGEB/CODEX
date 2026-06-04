# RTM Merge and Reference Layer

`docs/RTM/` is a merge/reference layer for PR-000 governance bootstrap traceability material. It does not define a new RTM schema and does not replace the existing RTM owners.

## Canonical sources

- `docs/rtm/` owns repository RTM bridge reports and local RTM lineage notes.
- `01_requirements/RTM.csv` owns the requirements traceability matrix data.

## Reconciliation action

PR-000 RTM concepts should be merged by reference into the canonical RTM surfaces. Use this directory to document mapping and onboarding context only. Any executable or data-bearing RTM update should land in the canonical RTM files instead of creating a parallel schema here.

## Bridge usage

1. Use `01_requirements/RTM.csv` for requirement rows, verification classes, deliverables, and source references.
2. Use `docs/rtm/` for bridge reports and lineage summaries.
3. Add references from this layer when PR-000 governance bootstrap concepts need to be reconciled with existing traceability.
4. Avoid duplicate CSV layouts, duplicate row identifiers, or alternate verification taxonomy.
