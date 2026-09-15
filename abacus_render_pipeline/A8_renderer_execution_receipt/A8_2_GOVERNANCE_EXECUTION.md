# A8.2 Governance Execution

## State

A8.2 is a controlled schema/governance mutation with renderer implementation, so the governing PR is classified as `TYPE: GOVERNANCE` with `SCHEMA MUTATION: CONTROLLED`.

## First red

The first W003 re-entry classified the PR as `TYPE: RENDERER` while declaring a controlled schema mutation. The governance parser correctly rejected that combination with:

`Unauthorized schema mutation outside GOVERNANCE type.`

This was a PR-metadata classification defect, not a renderer or receipt-runtime defect.

## Repair

The PR governance header now declares:

- `TYPE: GOVERNANCE`
- `SCHEMA MUTATION: CONTROLLED`

The implementation itself is unchanged by this repair.

## Exact-head re-entry requirement

The repaired head must independently rerun and pass:

1. W003 Governance Gate;
2. ABACUS Semantic Runtime;
3. production PPTX + PDF execution;
4. multi-format independent receipt validation;
5. cross-format parity;
6. atomic bundle promotion receipt;
7. deterministic/tamper tests;
8. normal CODEX render/security/governance checks applicable to the delta.

No PASS from the pre-repair head is promoted across this metadata repair without exact-head rerun evidence.

## Authority boundary

Generated PPTX/PDF remain non-canonical derivatives. A8.2 governs publication evidence only; it transfers no engineering, compliance, acceptance, negotiation or release authority.
