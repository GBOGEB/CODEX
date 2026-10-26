# qps_contract_canonicalization — Parity Matrix (CODEX ↔ cryoplant-project)

**Date:** 2026-10-26 · **Scope:** non-destructive assimilation (no files deleted in either repo)

CODEX holds **11** files, cryoplant-project holds **27**. They share a directory
name and three file names (`schema.ts`, `validate.ts`, `schema.test.ts`) that
**mean different (overlapping) contracts** — a federation hazard this assimilation
surfaces explicitly. `threeP3Schema.ts` is byte-identical in both.

## 1. File-by-file matrix

| File | CODEX | cryoplant | Status |
|------|:----:|:---------:|--------|
| `src/threeP3Schema.ts` | ✅ | ✅ | **IDENTICAL** (genuine shared module) |
| `src/schema.ts` | ✅ | ✅ | **NAME COLLISION / different contract** — CODEX=`FederationContract`; cryoplant=`CanonicalSsotSchema`+`UtilityGraphPayloadSchema` |
| `src/validate.ts` | ✅ | ✅ | **Different** — CODEX validates `federation_contract.json`; cryoplant validates `canonical_review_ssot.json` + `pvps_playground_contract.json`, emits sha256 receipt |
| `src/schema.test.ts` | ✅ | ✅ | **Different** — same 3 shared invariants on CODEX side; cryoplant adds utility-graph + PVPS tests |
| `package.json` | ✅ | ✅ | **Different** — cryoplant adds `yaml` dep, `@types/node`, 4 extra `validate:*` scripts |
| `src/mcpRuntimeSchema.ts` (+`.test`) | ✅ | ❌ | **CODEX-only** (MCP runtime) |
| `src/meshClosureControllerSchema.ts` (+`.test`), `src/validateMeshClosureController.ts` | ✅ | ❌ | **CODEX-only** (mesh closure controller) |
| `ssot/federation_contract.json` | ✅ | ❌ | **CODEX-only** fixture |
| `src/component_runtime_schema.ts` (+`.test`) | ❌ | ✅ | **cryoplant-only** |
| `src/global_adr_ocd_schema.ts`, `src/validate_global_adr_ocd.ts` | ❌ | ✅ | **cryoplant-only** |
| `src/hepak_workbench_schema.ts`, `hepak_workbench_receipt_schema.ts`, `validate_hepak_workbench.ts` | ❌ | ✅ | **cryoplant-only** |
| `src/interface_card_tp_schema.ts` (+`.test`), `src/validate_interface_card_tp.ts` | ❌ | ✅ | **cryoplant-only** |
| `src/linebRoundtripSchema.ts` | ❌ | ✅ | **cryoplant-only** |
| `src/n_type_manifest_schema.ts` (+`.test`) | ❌ | ✅ | **cryoplant-only** |
| `src/pvpsPlaygroundSchema.ts`, `src/validatePvpsPlayground.ts`, `pvps_playground.html` | ❌ | ✅ | **cryoplant-only** |
| `src/w111_power_utility_ssot_schema.ts`, `src/validate_w111_power_utility_ssot.ts` | ❌ | ✅ | **cryoplant-only** |
| `ssot/canonical_review_ssot.json`, `ssot/propagation_hooks.json`, `ssot/pvps_playground_contract.json` | ❌ | ✅ | **cryoplant-only** fixtures |
| `package-lock.json` | ❌ | ✅ | cryoplant-only |

## 2. Schema/function differences on the shared `Requirement` concept

| Aspect | CODEX `Requirement` | cryoplant `RequirementSchema` | Superset (this PR) |
|--------|--------------------|-------------------------------|--------------------|
| id / canonicalId / semanticGroupKey | ✅ | ✅ | ✅ |
| applicability / complianceStatus / scoreEligible / reviewWeight / scopeTags | ✅ | ✅ | ✅ |
| override-evidence field name | `overrideEvidence` | `applicabilityOverrideEvidence` | **accepts both**, reconciles to `applicabilityOverrideEvidence` |
| `sourceOccurrences` (provenance) | ❌ | required (≥1) | optional (preserved, must be ≥1 if present) |
| `aliasOf` / `mergedInto` / `supersededBy` | ❌ | ✅ | ✅ |
| removed-scope expression | `removedScopeTags[]` | `scopeDecisions[]` (REMOVED) | **accepts both**, reconciled via `resolveRemovedScope()` |
| Invariant: excluded applicability ⇒ NOT_SCORED/weight0/¬eligible | ✅ | ✅ | ✅ (shared) |
| Invariant: no duplicate score-eligible canonical/semantic | ✅ | ✅ | ✅ (shared) |
| Invariant: removed scope resurrection needs evidence | ✅ | ✅ | ✅ (shared) |
| Invariant: alias/merged ⇒ not score-eligible | ❌ | ✅ | ✅ (adopted) |
| Invariant: SUPERSEDED ⇒ supersededBy | ❌ | ✅ | ✅ (adopted) |

## 3. Parity on shared fixtures (verified, `npm test` = 12/12)

Both repos' SSOT fixtures canonicalize the **same** requirement population —
`RTM-045`, `RTM-046`, `RTM-047` (LN2/QSN obsolete rows). `canonicalParity.test.ts`
feeds that population in **both** field shapes through the superset and proves:

- **Converges:** `canonicalIds`, `sourceRows` (3), `denominatorCount` (**0**),
  `excludedCount` (**3**), `removedScopeLeak` (**0**), reconciled `removedScopeTags`
  are **identical** regardless of which repo's field shape is used.
- **Shared invariants agree:** removed-scope resurrection and duplicate
  score-eligible canonical are rejected in **both** shapes.
- **Documented divergence (real, not papered over):** cryoplant's `RTM-046` and
  `RTM-047` carry an extra `LN2_PRECOOL` scopeTag absent from CODEX's
  `federation_contract.json`. It does not change scoring (all rows OBSOLETE), but
  it is a genuine content delta the test asserts explicitly.

## 4. Recommendation

- **Canonical home for the requirement/federation contract:** CODEX (governance
  plane). This PR adds the reconciled **superset** (`src/canonicalParity.ts`) +
  parity tests. The cryoplant copy is **not** deleted.
- **Engineering SSOT modules** (utility graph, PVPS, HEPAK, interface cards,
  W111, N-type, global ADR/OCD) remain authored in cryoplant-project (engineering
  release authority). They are cryoplant-only and should stay there; a follow-up
  can lift any that need federation-level governance into CODEX under the same
  superset pattern.
- **Fix the name collision:** the two `schema.ts`/`validate.ts` should be renamed
  to reflect their distinct contracts (e.g. `federationSchema.ts` vs
  `engineeringSsotSchema.ts`) to remove cross-repo ambiguity.
- A companion cryoplant PR adds a README pointer to this canonical superset.
