# QSVG-P1B C2 visual-control closeout — v0.8.3

## Final disposition

`C2_VISUAL_CONTROL = CLOSED_PASS_EXACT_HEAD_REPEAT`

This closeout is limited to visual-control semantics. It grants no engineering/SAT/OPEX/negotiation/release authority.

## Evidence correction retained

The first workflow version named its checkout step “exact SHA” but used default `actions/checkout` pull-request behavior. Those runs exercised the synthetic PR merge ref and are retained only as integration evidence.

The repaired workflow explicitly checks out the PR head SHA, records `git rev-parse HEAD`, and fails unless they match.

## Final semantic contract enforced

1. Persistent local layer state with governed reset-to-default.
2. Explicit collision-box contract for exclusive annotation/legend regions.
3. Fail-closed executable checker.
4. Big teaching arrows OFF by default.
5. Dotted endpoint guides present.
6. Pressure overlay absent/deferred.
7. A/B/D/E semantic labels present.
8. Temperature heat-map label present.
9. Nominal 50 K shield uses one authoritative 50 K colour.
10. Right-to-left heat paths use direction-correct gradients.
11. A/B dark-card text uses explicit white contrast.
12. Outer parasitic endpoint markers terminate orange.
13. Inner 50→2 K endpoint markers terminate authoritative 2 K blue (`#0618aa`).

## Exact-head repeat evidence

### Final-semantics A

- subject head: `c2722c6e82b9fc189e7ce7bbdeb15254c0fb0f52`
- run: `34840954601`
- job: `103965576478`
- result: **PASS**
- exact subject checkout: success
- explicit SHA equality assertion: success
- strengthened visual-control checker: success

### Final-semantics B — distinct SHA

- subject head: `8b326c1be3e33e094cf1bb74eb23c28a6fc751c1`
- run: `34841132734`
- job: `103966131277`
- result: **PASS**
- exact subject checkout: success
- explicit SHA equality assertion: success
- strengthened visual-control checker: success

No canonical SVG/HTML/SSOT semantic change was introduced between A and B; B is the required distinct-head repeat.

## BD contraction

- `QSVG-BD-003` → `CLOSED_PASS_EXACT_HEAD_REPEAT`
- `QSVG-BD-004` → `CLOSED_PASS_EXACT_HEAD_REPEAT`
- `C2_VISUAL_CONTROL` → `CLOSED_PASS_EXACT_HEAD_REPEAT`

## Remaining core frontier

Only C3 remains on the local core path:
- `QSVG-BD-005` deterministic SSOT regeneration;
- `QSVG-BD-008` generator-bound canonical typed receipt.

`QSVG-BD-009` remains closed after post-review stable-artifact repeat.
`QSVG-BD-010 CONTROL` remains WITHHELD until C1 and C3 are formally closed.

Deferred/non-blocking: BD-006 pressure overlay and BD-007 hosted HTML.

Authority: `VISUAL_SEMANTIC_ONLY`.
