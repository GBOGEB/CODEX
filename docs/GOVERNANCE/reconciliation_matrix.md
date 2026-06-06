# Reconciliation Matrix — PR-000A Governance Bootstrap

**Branch:** `copilot/anthropic-gemini-integration`
**Date:** 2026-06-03
**Reconciliation ID:** PR-000A

## Overlap Summary

| Domain     | Overlap Score |
|------------|---------------|
| Governance | 76%           |
| RTM        | 72%           |
| DMAIC      | 74%           |
| ADR        | 68%           |
| Federation Reuse | 78%     |

## Artifact Action Table

| New Artifact    | Canonical Source                  | Action    | Bridge File                    |
|-----------------|-----------------------------------|-----------|--------------------------------|
| `docs/ADR`      | `06_arch/ADR/`                    | BRIDGE    | `docs/ADR/README.md`           |
| `docs/RTM`      | `docs/rtm/`, `01_requirements/RTM.csv` | MERGE     | `docs/RTM/README.md`           |
| `docs/GOVERNANCE` | `GOVERNANCE.md`, `DELTA_1/`, `KEB/governance/`, `MANIFEST/` | REFERENCE | `docs/GOVERNANCE/README.md` |
| `docs/DMAIC`    | `99_handover/PROCESS_DMAIC.md`    | BRIDGE    | `docs/DMAIC/README.md`         |

## Reconciliation Actions

### ADR → BRIDGE
- `docs/ADR/README.md` created as navigation, onboarding, and reference layer.
- No templates duplicated. All authoring deferred to `DELTA_1/governance_adr_template.md`.
- ADR records remain authoritative in `06_arch/ADR/ADR.md`.

### RTM → MERGE
- `docs/RTM/README.md` created as merge/reference layer.
- Canonical ownership preserved in `01_requirements/RTM.csv`.
- Local delta lineage referenced from `docs/rtm/local_rtm_lineage.md`.
- Incubator bridge referenced from `docs/rtm/incubator_rtm_bridge.md`.
- No parallel RTM schema created.

### GOVERNANCE → REFERENCE
- `docs/GOVERNANCE/README.md` created as federation index and navigation hub.
- Governance authority not redefined. Root authority deferred to `GOVERNANCE.md`.
- DELTA_1, KEB/governance, and MANIFEST listed as canonical federation members.

### DMAIC → BRIDGE
- `docs/DMAIC/README.md` created as quick-start guide and federation bridge.
- DMAIC lifecycle definitions not duplicated.
- Canonical lifecycle deferred to `99_handover/PROCESS_DMAIC.md`.

## Remaining Duplication Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| `GOVERNANCE.md` absent at repo root | Medium | Create or verify root `GOVERNANCE.md` before PR-001 |
| Multiple RTM references may diverge | Low | Enforce `01_requirements/RTM.csv` as single source of truth in PR review gates |
| ADR template in `DELTA_1/` not yet linked from `06_arch/ADR/` | Low | Add cross-reference in `06_arch/ADR/ADR.md` |
| `docs/GOVERNANCE/README.md` could attract new authoritative content | Low | Add governance lint check to CI if governance expands |

## Recommendation

**NEEDS REVIEW**

Root `GOVERNANCE.md` is absent. The federation index (`docs/GOVERNANCE/README.md`) references it but it does not exist. Confirm whether governance authority is embedded in `DELTA_1/` or `KEB/governance/` and create `GOVERNANCE.md` at repo root, or update the navigation hub to reflect the actual authoritative source before any push.
