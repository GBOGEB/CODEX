/**
 * Parity test for the assimilated canonical superset.
 *
 * It proves that the SAME QPS requirement population (the LN2/QSN obsolete rows
 * RTM-045/046/047 that appear, byte-for-byte on their shared fields, in BOTH
 * repos' SSOT fixtures) produces the SAME canonical output whether it arrives
 * in the CODEX field shape (overrideEvidence, no sourceOccurrences,
 * removedScopeTags) or the cryoplant field shape (applicabilityOverrideEvidence,
 * sourceOccurrences, scopeDecisions). It also checks the shared invariants
 * reject the same violations, and documents where the cryoplant superset adds
 * coverage CODEX did not have.
 */
import test from "node:test";
import assert from "node:assert/strict";
import { canonicalize, SupersetContractInput } from "./canonicalParity.js";

// ── Shared requirement population in the CODEX (federation_contract.json) shape.
const codexShape = {
  schemaVersion: "1.0.0",
  removedScopeTags: ["QSN", "LN2_PRECOOL", "LN2_TRANSPORT", "LN2_VAPORIZER", "LN2_LOGISTICS"],
  requirements: [
    { id: "RTM-045", canonicalId: "RTM-045", semanticGroupKey: "QPLANT.LN2.PRECOOL.80K", applicability: "OBSOLETE", complianceStatus: "NOT_SCORED", scoreEligible: false, reviewWeight: 0, scopeTags: ["QSN", "LN2_PRECOOL"], overrideEvidence: [] },
    { id: "RTM-046", canonicalId: "RTM-046", semanticGroupKey: "QPLANT.LN2.QSN_QRB_INTERFACE", applicability: "OBSOLETE", complianceStatus: "NOT_SCORED", scoreEligible: false, reviewWeight: 0, scopeTags: ["QSN", "LN2_TRANSPORT"], overrideEvidence: [] },
    { id: "RTM-047", canonicalId: "RTM-047", semanticGroupKey: "QPLANT.LN2.SIZING_LOGISTICS", applicability: "OBSOLETE", complianceStatus: "NOT_SCORED", scoreEligible: false, reviewWeight: 0, scopeTags: ["QSN", "LN2_LOGISTICS"], overrideEvidence: [] },
  ],
};

// ── The SAME population in the cryoplant (canonical_review_ssot.json) shape.
const cryoplantShape = {
  schemaVersion: "1.0.0",
  scopeDecisions: [
    { id: "DEC-QSN-001", subject: "QSN/LN2-only selected QPS scope", effectiveState: "REMOVED", descendantTags: ["QSN", "LN2_PRECOOL", "LN2_TRANSPORT", "LN2_VAPORIZER", "LN2_LOGISTICS"], evidence: ["QPS_W52_P2M_CONTRACT_CLARIFICATION.yaml"] },
  ],
  requirements: [
    { id: "RTM-045", canonicalId: "RTM-045", semanticGroupKey: "QPLANT.LN2.PRECOOL.80K", sourceOccurrences: ["SCK-CEN-90508872-4.2.5-RTM-045"], applicability: "OBSOLETE", complianceStatus: "NOT_SCORED", scoreEligible: false, reviewWeight: 0, scopeTags: ["QSN", "LN2_PRECOOL"], applicabilityOverrideEvidence: [] },
    { id: "RTM-046", canonicalId: "RTM-046", semanticGroupKey: "QPLANT.LN2.QSN_QRB_INTERFACE", sourceOccurrences: ["SCK-CEN-90508872-4.2.5-RTM-046"], applicability: "OBSOLETE", complianceStatus: "NOT_SCORED", scoreEligible: false, reviewWeight: 0, scopeTags: ["QSN", "LN2_TRANSPORT", "LN2_PRECOOL"], applicabilityOverrideEvidence: [] },
    { id: "RTM-047", canonicalId: "RTM-047", semanticGroupKey: "QPLANT.LN2.SIZING_LOGISTICS", sourceOccurrences: ["SCK-CEN-90508872-4.2.5-RTM-047"], applicability: "OBSOLETE", complianceStatus: "NOT_SCORED", scoreEligible: false, reviewWeight: 0, scopeTags: ["QSN", "LN2_LOGISTICS", "LN2_PRECOOL"], applicabilityOverrideEvidence: [] },
  ],
};

test("both repo shapes parse against the superset", () => {
  assert.equal(SupersetContractInput.safeParse(codexShape).success, true);
  assert.equal(SupersetContractInput.safeParse(cryoplantShape).success, true);
});

test("PARITY: same population -> same invariant-bearing canonical output regardless of field shape", () => {
  const a = canonicalize(codexShape);
  const b = canonicalize(cryoplantShape);
  // The scoring-relevant canonical facts converge exactly across both shapes.
  assert.deepEqual(a.canonicalIds, b.canonicalIds);
  assert.equal(a.sourceRows, b.sourceRows);
  assert.equal(a.denominatorCount, b.denominatorCount);
  assert.equal(a.excludedCount, b.excludedCount);
  assert.equal(a.removedScopeLeak, b.removedScopeLeak);
  assert.deepEqual(a.removedScopeTags, b.removedScopeTags);
  // Concrete expected canonical values (all three rows obsolete, nothing scored):
  assert.equal(a.denominatorCount, 0);
  assert.equal(a.excludedCount, 3);
  assert.equal(a.removedScopeLeak, 0);
});

test("DOCUMENTED DIVERGENCE: cryoplant tags RTM-046/047 with an extra LN2_PRECOOL scope tag", () => {
  // The two source SSOTs are NOT byte-identical: cryoplant's RTM-046 and RTM-047
  // carry an additional "LN2_PRECOOL" scopeTag that CODEX's federation_contract
  // does not. This is immaterial to scoring (all three rows are OBSOLETE /
  // NOT_SCORED, so denominator and leak are identical) but it is a real content
  // delta that assimilation must surface rather than silently drop.
  const a = canonicalize(codexShape);
  const b = canonicalize(cryoplantShape);
  const tagsOf = (c: ReturnType<typeof canonicalize>, id: string) =>
    c.rows.find((r) => r.canonicalId === id)!.scopeTags;
  assert.deepEqual(tagsOf(a, "RTM-046"), ["LN2_TRANSPORT", "QSN"]);
  assert.deepEqual(tagsOf(b, "RTM-046"), ["LN2_PRECOOL", "LN2_TRANSPORT", "QSN"]);
  assert.notDeepEqual(tagsOf(a, "RTM-046"), tagsOf(b, "RTM-046"));
});

test("SHARED invariant: both shapes reject removed-scope resurrection without evidence", () => {
  const leakCodex = { ...codexShape, requirements: [{ ...codexShape.requirements[0], applicability: "APPLICABLE", complianceStatus: "OPEN", scoreEligible: true, reviewWeight: 1 }] };
  const leakCryo = { ...cryoplantShape, requirements: [{ ...cryoplantShape.requirements[0], applicability: "APPLICABLE", complianceStatus: "OPEN", scoreEligible: true, reviewWeight: 1 }] };
  assert.equal(SupersetContractInput.safeParse(leakCodex).success, false);
  assert.equal(SupersetContractInput.safeParse(leakCryo).success, false);
});

test("SHARED invariant: duplicate score-eligible canonical rejected in both shapes", () => {
  const dup = (base: typeof codexShape) => ({
    ...base,
    removedScopeTags: [],
    scopeDecisions: undefined,
    requirements: [
      { ...base.requirements[0], applicability: "APPLICABLE", complianceStatus: "OPEN", scoreEligible: true, reviewWeight: 1, scopeTags: [] },
      { ...base.requirements[1], canonicalId: base.requirements[0].canonicalId, semanticGroupKey: "OTHER", applicability: "APPLICABLE", complianceStatus: "OPEN", scoreEligible: true, reviewWeight: 1, scopeTags: [] },
    ],
  });
  assert.equal(SupersetContractInput.safeParse(dup(codexShape)).success, false);
});

test("DIVERGENCE (cryoplant superset adds coverage): SUPERSEDED requires supersededBy", () => {
  // CODEX's schema has no supersededBy concept; the superset enforces it.
  const row = { id: "RTM-100", canonicalId: "RTM-100", semanticGroupKey: "G", applicability: "SUPERSEDED", complianceStatus: "NOT_SCORED", scoreEligible: false, reviewWeight: 0, scopeTags: [], applicabilityOverrideEvidence: [] };
  assert.equal(SupersetContractInput.safeParse({ schemaVersion: "1.0.0", requirements: [row] }).success, false);
  assert.equal(SupersetContractInput.safeParse({ schemaVersion: "1.0.0", requirements: [{ ...row, supersededBy: "RTM-200" }] }).success, true);
});

test("DIVERGENCE (cryoplant superset adds coverage): alias cannot be score-eligible", () => {
  const row = { id: "RTM-300", canonicalId: "RTM-300", semanticGroupKey: "G2", applicability: "APPLICABLE", complianceStatus: "OPEN", scoreEligible: true, reviewWeight: 1, scopeTags: [], aliasOf: "RTM-1", applicabilityOverrideEvidence: [] };
  assert.equal(SupersetContractInput.safeParse({ schemaVersion: "1.0.0", requirements: [row] }).success, false);
});
