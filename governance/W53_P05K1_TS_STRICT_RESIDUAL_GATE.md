# W53/P05K1 — CODEX strict-residual validator

## Intent
Validate semantics, independence, provenance and tolerance before the P05K1 thermal-shield receipt may re-enter the QPS child.

## Candidate boundary
- ALAT current non-binding example: D 14.12 bara/35 K -> E 13.12 bara/55 K.
- ALAT example enthalpies: 196438 -> 302915 J/kg.
- Contract Table 8: 8200 W.
- Contract Table 9: D/E approximately 77 g/s.

## Mandatory predicates
1. Exact ALAT source locator present and hash-bound.
2. `non_binding=true` retained for exact D/E state.
3. Contract mass-flow source independently bound.
4. ALAT reconstructed 77.01 g/s tagged `DERIVED_NON_INDEPENDENT`.
5. Exact-state property receipt from CoolProp 7.2.0 present.
6. Independent property-reference receipt present or explicit DEFER.
7. Same control volume demonstrated.
8. Flow tolerance semantics predeclared before PASS evaluation.
9. Residual W/% and inverse-flow residual emitted.
10. No topology identity counted as residual.
11. No historic source promoted over current offer.
12. Child remains sole compliance authority.

## Required negative tests
Reject: rounded-state substitution; reconstructed bidder flow represented as independent; provider self-validation; missing-source imputation; post-hoc tolerance; non-binding-to-guarantee promotion; parent self-acceptance.

## Quantitative validator metrics
Emit source-bound %, provenance %, independent-reference %, same-boundary completeness %, provider disagreement %, residual %, uncertainty width, negative-test pass fraction, first-pass yield and retry count.

## PCA/BT rule
Only observed validator outputs may enter PCA. Planning scores remain outside the PCA matrix. BT pairwise ranking may guide work but cannot alter residual disposition.

## Disposition
- `PASS_TO_CHILD_REENTRY`: every mandatory predicate true and residual within predeclared tolerance.
- `DEFER_INDEPENDENT_REFERENCE`: numerical receipt complete but independent property reference absent/unproven.
- `DEFER_TOLERANCE_SEMANTICS`: approximate contract flow not governed tightly enough.
- `REJECT_SOURCE_CIRCULARITY`: purported residual depends on derived bidder flow or same-source identity.
- `REJECT_BOUNDARY_MISMATCH`: P/T/Q/mdot do not describe the same control volume.

## Victory
A mechanically validated, independently evidenced residual candidate reaches child re-entry without CODEX assigning compliance credit.
