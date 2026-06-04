# RTM Merge Pointer

`docs/RTM/` is a MERGE pointer only. It preserves discoverability for contributors who look for uppercase RTM documentation, but canonical RTM ownership remains elsewhere.

## Canonical Authority

| Need | Canonical source |
|---|---|
| Requirement table and fields | `01_requirements/RTM.csv` |
| Runtime/federation RTM lineage | `docs/rtm/` |

## Merge Rule

- Do not create requirement rows, RTM schemas, or second CSV files here.
- Put new requirement rows in `01_requirements/RTM.csv`.
- Put runtime/federation lineage notes in `docs/rtm/`.
- Use this uppercase path only as a temporary pointer until maintainers approve casing consolidation.

## PR-000A Status

Action: **MERGE**. Residual duplication target after reconciliation: **12%**.
