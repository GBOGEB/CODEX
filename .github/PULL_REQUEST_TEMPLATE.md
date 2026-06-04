# PR-000 Governance Bootstrap Checklist

## Summary

Describe the change, the governance area affected, and the expected operational outcome.

## Scope

- [ ] Governance policy or process
- [ ] Requirements traceability matrix (RTM)
- [ ] DMAIC quality loop
- [ ] Architecture Decision Record (ADR)
- [ ] Security or contributor workflow
- [ ] Documentation-only change

## Canonical Source Traceability

Identify the existing source of authority before adding or changing governance artifacts. New docs should bridge, merge, or reference canonical sources rather than creating parallel authority.

| Item | Canonical Source / Evidence |
|---|---|
| Related requirement / RTM row | `01_requirements/RTM.csv` or `docs/rtm/` |
| Related ADR | `06_arch/ADR/` or `DELTA_1/governance_adr_template.md` |
| Related DMAIC phase | `99_handover/PROCESS_DMAIC.md` or `maps/dmaic_phase_map.yml` |
| Governance authority | `GOVERNANCE.md`, `DELTA_1/`, `KEB/governance/`, or `MANIFEST/` |
| Risk / control reference | |

## Validation Evidence

List exact commands, generated artifacts, and review evidence used to validate this change.

```text
# command output or artifact paths
```

## Governance Review

- [ ] Change is limited to the stated scope.
- [ ] Documentation paths and owners are clear and reference canonical sources.
- [ ] Security implications have been considered.
- [ ] Required follow-up actions are captured.
