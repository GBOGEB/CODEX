# W53/P05K1 — KEB strict-residual validation gate

## Mission

CODEX validates whether the proposed thermal-shield residual is genuinely independent, same-boundary, source-bound and eligible for child disposition. It does not award compliance.

## Candidate

Current ALAT non-binding TS example, C1462-TN-001 pages 59–60:

- D = 14.12 bara / 35 K;
- E = 13.12 bara / 55 K;
- QTS = 8200 W;
- bidder hD = 196438 J/kg;
- bidder hE = 302915 J/kg;
- bidder reconstructed mdot = 77.01 g/s.

Contract independent anchor: Table 9 D/E approximately 77 g/s. Contract Table 8 QTS = 8200 W.

## Mandatory validation predicates

1. `EXACT_STATE_BOUND`: exact 14.12/35 -> 13.12/55 state used.
2. `SOURCE_LOCATOR_BOUND`: ALAT pages 59–60 and controlled child source object present.
3. `AUTHORITY_PRESERVED`: non-binding example remains non-binding.
4. `FLOW_INDEPENDENCE`: primary residual uses contract ≈77 g/s, not bidder reconstructed 77.01 g/s.
5. `PROPERTY_INDEPENDENCE`: at least two genuinely independent property bases, or explicit DEFER.
6. `SAME_CONTROL_VOLUME`: duty, flow and enthalpy endpoints describe D->E thermal-shield boundary.
7. `TOLERANCE_PREDECLARED`: tolerance semantics recorded before PASS disposition.
8. `NO_TOPOLOGY_IDENTITY`: no A=B+W-style identity accepted as residual.
9. `NO_PARENT_SELF_PROMOTION`: KEB validation returns evidence only.
10. `NEGATIVE_TESTS_PASS`: circular-source, rounded-state, historic-override and missing-property fixtures reject.

## KEB disposition

Allowed outputs:

- `VALID_STRICT_RESIDUAL_CANDIDATE`;
- `DEFER_INDEPENDENT_PROPERTY_REFERENCE`;
- `DEFER_TOLERANCE_SEMANTICS`;
- `REJECT_SOURCE_CIRCULARITY`;
- `REJECT_BOUNDARY_MISMATCH`;
- `REJECT_AUTHORITY_PROMOTION`.

## Quantitative validation fields

The validated receipt must carry:

- provider/version and source SHA;
- hD/hE/Δh per provider;
- predicted Q at governed flow points;
- Q residual W/%;
- inverse predicted flow and residual g/s;
- provider disagreement %;
- independent-reference coverage %;
- provenance completeness %;
- observed-vs-planning classification for PCA/BT features.

## PCA/BT guard

PCA rows derived from this wave must contain observed values only. Any planning score makes the population `HYBRID_OBSERVED_PLUS_PLANNING` and ineligible for statistical action selection.

BT pairwise scores shall expose the evidence supporting each comparison. Priority does not imply acceptance.

## Victory

Return a mechanically valid candidate to the QPS child. Only the child may convert it to strict residual `1/5`.