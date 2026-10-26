/**
 * Canonical Requirement parity / superset (assimilation of the two
 * qps_contract_canonicalization implementations).
 *
 * BACKGROUND
 * ----------
 * Two repositories independently canonicalize the SAME underlying QPS
 * requirement population but with different schema shapes:
 *
 *   - CODEX  (governance / federation plane)   src/schema.ts -> `FederationContract`
 *       Requirement fields: id, canonicalId, semanticGroupKey, applicability,
 *       complianceStatus, scoreEligible, reviewWeight, scopeTags,
 *       `overrideEvidence`.  Validates ssot/federation_contract.json.
 *
 *   - cryoplant-project (engineering SSOT plane) src/schema.ts -> `CanonicalSsotSchema`
 *       Requirement fields: the CODEX set PLUS `sourceOccurrences` (required),
 *       `aliasOf`, `mergedInto`, `supersededBy`, and the override-evidence field
 *       is named `applicabilityOverrideEvidence`.  Validates
 *       ssot/canonical_review_ssot.json (with scopeDecisions + artifacts).
 *
 * The field name `schema.ts` therefore collides across the two repos while
 * meaning two different (overlapping) contracts. This module reconciles the
 * requirement concept into a single SUPERSET that:
 *   1. accepts BOTH field shapes (overrideEvidence | applicabilityOverrideEvidence,
 *      optional sourceOccurrences), and
 *   2. enforces the UNION of invariants from both implementations.
 *
 * It also exposes `canonicalize()` which produces a stable, implementation-
 * independent canonical output, so a parity test can prove that the SAME
 * requirement population expressed in EITHER shape yields the SAME canonical
 * result (see canonicalParity.test.ts).
 */
import { z } from "zod";

export const Applicability = z.enum([
  "APPLICABLE",
  "NOT_APPLICABLE",
  "OBSOLETE",
  "SUPERSEDED",
  "PENDING_SCOPE_CONFIRMATION",
]);
export const ComplianceStatus = z.enum([
  "PASS",
  "PARTIAL",
  "FAIL",
  "OPEN",
  "NOT_SCORED",
]);

/**
 * Superset requirement input. Both repos' row shapes parse against this:
 *  - `overrideEvidence` (CODEX) and `applicabilityOverrideEvidence` (cryoplant)
 *    are accepted as aliases and reconciled to `applicabilityOverrideEvidence`.
 *  - `sourceOccurrences` is optional here (CODEX omits it; cryoplant requires
 *    >=1). When present it must be non-empty, preserving cryoplant's rule.
 */
export const SupersetRequirementInput = z
  .object({
    id: z.string().min(1),
    canonicalId: z.string().min(1),
    semanticGroupKey: z.string().min(1),
    applicability: Applicability,
    complianceStatus: ComplianceStatus,
    scoreEligible: z.boolean(),
    reviewWeight: z.number().nonnegative(),
    scopeTags: z.array(z.string()).default([]),
    // provenance / lineage (cryoplant superset)
    sourceOccurrences: z.array(z.string().min(1)).min(1).optional(),
    aliasOf: z.string().min(1).optional(),
    mergedInto: z.string().min(1).optional(),
    supersededBy: z.string().min(1).optional(),
    // override-evidence under either name
    overrideEvidence: z.array(z.string()).optional(),
    applicabilityOverrideEvidence: z.array(z.string()).optional(),
  })
  .transform((r) => {
    const evidence =
      r.applicabilityOverrideEvidence ?? r.overrideEvidence ?? [];
    return {
      id: r.id,
      canonicalId: r.canonicalId,
      semanticGroupKey: r.semanticGroupKey,
      applicability: r.applicability,
      complianceStatus: r.complianceStatus,
      scoreEligible: r.scoreEligible,
      reviewWeight: r.reviewWeight,
      scopeTags: r.scopeTags,
      sourceOccurrences: r.sourceOccurrences ?? null,
      aliasOf: r.aliasOf ?? null,
      mergedInto: r.mergedInto ?? null,
      supersededBy: r.supersededBy ?? null,
      applicabilityOverrideEvidence: evidence,
    };
  })
  .superRefine((r, ctx) => {
    // ── invariant shared by BOTH implementations ──
    const excluded = ["NOT_APPLICABLE", "OBSOLETE", "SUPERSEDED"].includes(
      r.applicability
    );
    if (
      excluded &&
      (r.scoreEligible ||
        r.reviewWeight !== 0 ||
        r.complianceStatus !== "NOT_SCORED")
    ) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: `${r.id}: excluded applicability must be NOT_SCORED, weight=0 and scoreEligible=false`,
      });
    }
    // ── invariants added by the cryoplant superset ──
    if ((r.aliasOf || r.mergedInto) && r.scoreEligible) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: `${r.id}: alias/merged requirement cannot be independently score eligible`,
      });
    }
    if (r.applicability === "SUPERSEDED" && !r.supersededBy) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: `${r.id}: SUPERSEDED requires supersededBy`,
      });
    }
  });

export type SupersetRequirement = z.infer<typeof SupersetRequirementInput>;

export const ScopeDecisionSchema = z.object({
  id: z.string().min(1),
  subject: z.string().min(1),
  effectiveState: z.enum(["ACTIVE", "REMOVED"]),
  descendantTags: z.array(z.string()).min(1),
  evidence: z.array(z.string()).min(1),
});

/**
 * Superset canonical contract. Accepts either:
 *  - a CODEX-style `removedScopeTags: string[]`, or
 *  - a cryoplant-style `scopeDecisions: ScopeDecision[]`,
 * and reconciles both into the same removed-scope set used for the shared
 * "removed scope resurrection" invariant.
 */
export const SupersetContractInput = z
  .object({
    schemaVersion: z.literal("1.0.0"),
    requirements: z.array(SupersetRequirementInput),
    removedScopeTags: z.array(z.string()).optional(),
    scopeDecisions: z.array(ScopeDecisionSchema).optional(),
  })
  .superRefine((s, ctx) => {
    const removed = resolveRemovedScope(s.removedScopeTags, s.scopeDecisions);

    // ── invariants shared by BOTH implementations ──
    const seenCanonical = new Set<string>();
    const seenSemantic = new Set<string>();
    for (const r of s.requirements.filter((x) => x.scoreEligible)) {
      if (seenCanonical.has(r.canonicalId)) {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          message: `duplicate score-eligible canonical ${r.canonicalId}`,
        });
      }
      if (seenSemantic.has(r.semanticGroupKey)) {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          message: `duplicate score-eligible semantic group ${r.semanticGroupKey}`,
        });
      }
      seenCanonical.add(r.canonicalId);
      seenSemantic.add(r.semanticGroupKey);

      if (
        r.scopeTags.some((t) => removed.has(t)) &&
        r.applicabilityOverrideEvidence.length === 0
      ) {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          message: `${r.id}: removed scope resurrected without evidenced override`,
        });
      }
    }
  });

export type SupersetContract = z.infer<typeof SupersetContractInput>;

/** Reconcile the two ways a contract can express "removed scope". */
export function resolveRemovedScope(
  removedScopeTags?: string[],
  scopeDecisions?: z.infer<typeof ScopeDecisionSchema>[]
): Set<string> {
  const removed = new Set<string>(removedScopeTags ?? []);
  for (const d of scopeDecisions ?? []) {
    if (d.effectiveState === "REMOVED") {
      for (const t of d.descendantTags) removed.add(t);
    }
  }
  return removed;
}

/**
 * Produce a STABLE, implementation-independent canonical summary of a contract.
 * Two contracts that describe the same requirement population — regardless of
 * which repo's field shape they came in — yield an identical object here.
 */
export function canonicalize(input: unknown) {
  const parsed = SupersetContractInput.parse(input);
  const rows = [...parsed.requirements].sort((a, b) =>
    a.canonicalId.localeCompare(b.canonicalId)
  );
  const scoreEligible = rows.filter((r) => r.scoreEligible);
  const excluded = rows.filter((r) => !r.scoreEligible);
  const removed = resolveRemovedScope(
    parsed.removedScopeTags,
    parsed.scopeDecisions
  );
  return {
    schemaVersion: parsed.schemaVersion,
    sourceRows: rows.length,
    denominatorCount: scoreEligible.length,
    excludedCount: excluded.length,
    removedScopeTags: [...removed].sort(),
    removedScopeLeak: scoreEligible.filter((r) =>
      r.scopeTags.some((t) => removed.has(t))
    ).length,
    canonicalIds: rows.map((r) => r.canonicalId),
    rows: rows.map((r) => ({
      canonicalId: r.canonicalId,
      semanticGroupKey: r.semanticGroupKey,
      applicability: r.applicability,
      complianceStatus: r.complianceStatus,
      scoreEligible: r.scoreEligible,
      reviewWeight: r.reviewWeight,
      scopeTags: [...r.scopeTags].sort(),
    })),
  };
}
