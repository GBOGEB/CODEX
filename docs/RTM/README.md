# RTM — Merge & Reference Layer

> **Status: MERGE**
> This directory merges concepts from multiple RTM sources.
> Canonical RTM ownership is preserved in the sources listed below.
> Do **not** create a parallel RTM schema here.

## Canonical Sources

| Source | Description |
|--------|-------------|
| [`01_requirements/RTM.csv`](../../01_requirements/RTM.csv) | Primary requirements traceability matrix |
| [`docs/rtm/local_rtm_lineage.md`](../rtm/local_rtm_lineage.md) | Local delta RTM lineage (Alpha A6) |
| [`docs/rtm/incubator_rtm_bridge.md`](../rtm/incubator_rtm_bridge.md) | Incubator → ABACUS RTM bridge report |

## Concept Merge Summary

This layer consolidates navigation to the above sources. Any additions to requirements traceability must be made in `01_requirements/RTM.csv` as the single authoritative record.

| Domain          | Canonical Location                    | Action             |
|-----------------|---------------------------------------|--------------------|
| Programme RTM   | `01_requirements/RTM.csv`             | Authoritative — do not replicate |
| Local A6 deltas | `docs/rtm/local_rtm_lineage.md`       | Reference here     |
| Incubator bridge| `docs/rtm/incubator_rtm_bridge.md`    | Reference here     |

## References

- [01_requirements/RTM.csv](../../01_requirements/RTM.csv)
- [docs/rtm/](../rtm/)

> **Reconciliation Note:** Overlap with `docs/rtm/` and `01_requirements/RTM.csv` measured at 72%.
> This layer was converted from an authoritative source to a merge/reference layer
> as part of PR-000A Governance Bootstrap Reconciliation.
