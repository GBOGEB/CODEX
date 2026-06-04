# ADR Bridge and Reference Layer

`docs/ADR/` is a navigation, onboarding, and reference layer only. It is not the authoritative ADR source and must not introduce duplicate ADR templates or a parallel ADR numbering scheme.

## Canonical sources

- `06_arch/ADR/` owns repository ADR records.
- `DELTA_1/governance_adr_template.md` owns the governance ADR template pattern.

## Reconciliation action

Use this directory to point readers to canonical ADR materials and to explain how PR-000 governance bootstrap artifacts map into existing ADR ownership. New ADRs should be created in the canonical ADR location, using the canonical template where governance-specific structure is required.

## Bridge usage

1. Start with `06_arch/ADR/` for accepted architectural decisions.
2. Use `DELTA_1/governance_adr_template.md` for governance ADR formatting.
3. Reference PR-000 bootstrap notes from here only when they help onboarding or migration review.
4. Do not copy ADR templates into this directory.
