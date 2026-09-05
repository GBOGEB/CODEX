# W53/P05K1 — CODEX strict TS residual validation gate

## Mission

Validate whether the ABACUS thermal-shield receipt is genuinely independent, same-boundary, source-bound and eligible for child disposition. CODEX does not award compliance.

## Required evidence tuple

`{contract_QTS, contract_mdot_semantics, bidder_D_state, bidder_E_state, property_provider_A, independent_property_provider_B, tolerance_policy, receipt_hash}`

Required exact bidder state:

- D = 14.12 bara / 35 K;
- E = 13.12 bara / 55 K;
- source = ALAT C1462-TN-001 pages 59–60;
- source authority = current-offer non-binding thermodynamic example.

Contract anchors:

- QTS = 8200 W;
- D/E flow approximately 77 g/s.

## Validation predicates

1. `same_control_volume == true`.
2. `current_offer_state_exact == true`.
3. `contract_flow_is_independent_of_bidder_enthalpy == true`.
4. `bidder_77p01_not_used_as_independent_flow == true`.
5. `provider_A != provider_B` by implementation/data lineage, not merely alias/version.
6. `tolerance_predeclared == true`.
7. `nonbinding_example_not_promoted_to_guaranteed_BOP == true`.
8. `historic_source_not_promoted_to_current_authority == true`.
9. `receipt_source_hashes_present == true`.
10. `child_disposition_required == true`.

## Quantitative checks

For every provider emit:

- hD, hE, delta_h;
- Q at 76.5/77.0/77.5 g/s;
- residual W and % against 8200 W;
- inverse mdot at 8200 W;
- provider disagreement in delta_h and inverse mdot.

The ALAT table itself shall be checked separately for internal consistency using 77.01 g/s and bidder h values. That row is evidence of bidder calculation consistency, not independent residual proof.

## Fail-closed outcomes

- `REJECT_SOURCE_CIRCULARITY` if bidder reconstructed flow is paired with bidder enthalpy/duty and called independent.
- `DEFER_PROPERTY_REFERENCE` if only CoolProp is available.
- `DEFER_TOLERANCE_SEMANTICS` if approximate 77 g/s has no governed interpretation.
- `REJECT_BOUNDARY_MUTATION` if rounded 14/40 -> 13/60 substitutes for exact 14.12/35 -> 13.12/55.
- `DEFER_SOURCE_HASH` if exact source locator/hash is absent.
- `PASS_TO_CHILD_DISPOSITION` only when all semantic gates pass.

## Regression tests

Negative fixtures shall deliberately attempt:

- bidder 77.01 as independent flow;
- CoolProp compared with CoolProp under a second label;
- historic ALAT/LKT state promoted to current-offer state;
- rounded P/T boundary;
- post-hoc tolerance widening;
- parent ACCEPT without child authority.

Every negative fixture must fail closed.

## PCA / BT observation contract

Only measured receipt values enter PCA. Planning scores, manually assigned source-bound fractions and expected DoV gains are excluded from PCA observations. BT may use planning criteria but shall label them separately from measured pairwise outcomes.

## Victory

CODEX emits `PASS_TO_CHILD_DISPOSITION` with zero semantic/provenance mutation and a complete independent-evidence tuple. Anything less is an explicit DEFER/REJECT, never an implicit PASS.
