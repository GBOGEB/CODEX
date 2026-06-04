# PR-000A Governance Reconciliation Matrix

| New Artifact | Canonical Source | Action | Pre% | Post% |
|---|---|---|---:|---:|
| `docs/ADR` | `06_arch/ADR` | BRIDGE | 68 | 8 |
| `docs/RTM` | `docs/rtm` + `01_requirements/RTM.csv` | MERGE | 72 | 12 |
| `docs/GOVERNANCE` | `GOVERNANCE.md` + `DELTA_1/` + `KEB/governance/` + `MANIFEST/` | REFERENCE | 76 | 15 |
| `docs/DMAIC` | `99_handover/PROCESS_DMAIC.md` | BRIDGE | 74 | 8 |

## Measurement Basis

Post% measures residual duplication risk after removing standalone templates/schemas and converting the directories to pointer-only bridge, merge, or reference surfaces.

| Metric | Score |
|---|---:|
| Maximum residual overlap | 15 |
| Federation reuse score | 94 |

## Acceptance Result

All Post% values are <= 20 and the federation reuse score is >= 90.

Recommendation: **READY FOR PUSH** after maintainer review of the local commit and branch naming.
