# QSVG-P1B C2 visual-control closeout — v0.8.3

## Current disposition

`C2_VISUAL_CONTROL = CLOSE_CANDIDATE_FINAL_SEMANTICS_EXACT_HEAD_A_PASS`

This closeout is limited to visual-control semantics. It grants no engineering/SAT/OPEX/negotiation/release authority.

## Evidence correction retained

The first workflow version named its checkout step “exact SHA” but used default `actions/checkout` pull-request behavior. Those runs exercised the synthetic PR merge ref and are retained only as integration evidence.

The repaired workflow explicitly checks out the PR head SHA, records `git rev-parse HEAD`, and fails unless they match.

## Final semantic contract now enforced

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
13. Inner 50→2 K endpoint markers terminate authoritative 2 K blue (`#0618aa`), closing the final Codex P2 marker finding.

## Earlier exact-head evidence — pre-final marker semantics

- `817fd4a893c8078bb857dbca06788dcd5aabe534`
- run `34840579855`
- job `103964362990`
- PASS with explicit subject-SHA equality

Useful control evidence, but not counted as the final-semantics repeat pair because the inner endpoint marker repair landed later.

## Final-semantics exact-head evidence A

- subject head: `c2722c6e82b9fc189e7ce7bbdeb15254c0fb0f52`
- run: `34840954601`
- job: `103965576478`
- result: **PASS**
- exact subject checkout: success
- explicit SHA equality assertion: success
- strengthened visual-control checker v0.3.0: success

## Repeat B

This metadata-only closeout update intentionally creates a distinct head without changing canonical SVG/HTML/SSOT semantics. The triggered exact-head workflow is Repeat B.

Closure predicate:
- Repeat B PASS;
- explicit subject-SHA equality PASS;
- visual-control checker PASS.

Then:
- `QSVG-BD-003` → `CLOSED_PASS_EXACT_HEAD_REPEAT`
- `QSVG-BD-004` → `CLOSED_PASS_EXACT_HEAD_REPEAT`
- `C2_VISUAL_CONTROL` → `CLOSED_PASS_EXACT_HEAD_REPEAT`

## Remaining core frontier

After Repeat B, only C3 remains on the core path:
- `QSVG-BD-005` deterministic SSOT regeneration;
- `QSVG-BD-008` generator-bound canonical receipt.

`QSVG-BD-009` remains closed after post-review stable-artifact repeat.
`QSVG-BD-010 CONTROL` remains WITHHELD until C3 closes.

Deferred/non-blocking: BD-006 pressure overlay and BD-007 hosted HTML.

Authority: `VISUAL_SEMANTIC_ONLY`.
