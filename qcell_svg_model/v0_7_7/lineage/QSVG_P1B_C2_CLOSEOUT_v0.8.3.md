# QSVG-P1B C2 visual-control closeout — v0.8.3

## Corrected disposition

`C2_VISUAL_CONTROL = CLOSE_CANDIDATE_EXACT_HEAD_A_PASS`

This closeout is limited to visual-control semantics. It grants no engineering/SAT/OPEX/negotiation/release authority.

## Evidence correction

The first workflow version named its checkout step “exact SHA” but used the default `actions/checkout` pull-request behavior. Those runs therefore exercised the synthetic PR merge ref, not a proven exact head checkout. They remain useful integration evidence but are **not** counted as exact-head proof.

The workflow has now been repaired to:

- explicitly check out `github.event.pull_request.head.sha` on PR events;
- record `git rev-parse HEAD`;
- fail unless the checked-out SHA equals the requested subject SHA.

This correction narrows prior claims rather than silently retaining them.

## BD contraction

- `QSVG-BD-003 text/annotation collision control` → **CLOSE_CANDIDATE_EXACT_HEAD_A_PASS**
- `QSVG-BD-004 layer-state control` → **CLOSE_CANDIDATE_EXACT_HEAD_A_PASS**

## Implemented controls

1. Persistent local layer state with governed reset-to-default.
2. Explicit collision-box contract for exclusive annotation/legend regions.
3. Fail-closed executable checker.
4. CI workflow `QCELL SVG Visual Control`.
5. Big teaching arrows required OFF by default.
6. Dotted endpoint guides required present.
7. Pressure overlay required absent/deferred in current MAIN.
8. A/B/D/E values required present.
9. Temperature heat-map label required present.
10. Review-derived thermal semantic guards:
   - nominal 50 K shield uses one authoritative 50 K colour;
   - right-to-left parasitic heat paths use direction-correct reversed gradients;
   - A/B dark-card text contrast is explicitly white.

## Earlier PR-merge-ref evidence — retained but not exact-head credit

- `280c17e0...` / run `34839673188` / PASS
- `86e31ba3...` / run `34839729228` / PASS
- `deabaaacd...` / run `34840022581` / PASS with strengthened semantic checker

## Exact-head evidence A

- subject head: `817fd4a893c8078bb857dbca06788dcd5aabe534`
- run: `34840579855`
- job: `103964362990`
- result: **PASS**
- checkout exact subject SHA: success
- explicit SHA equality assertion: success
- fail-closed visual-control check: success

## Repeat requirement

One further distinct exact-head execution is required before labeling C2 `CLOSED_PASS_EXACT_HEAD_REPEAT`. This file update itself creates a distinct head and should trigger that repeat without modifying MAIN geometry or semantics.

## Remaining critical-path BD

After exact-head repeat, the active core lane contracts to **C3 PROOF_AND_REPEAT**:

- `QSVG-BD-005` clean YAML→SVG→HTML regeneration determinism;
- `QSVG-BD-008` generator-bound canonical visual receipt.

`QSVG-BD-009` stable-artifact repeat is already closed on P1A after review repair.
`QSVG-BD-010 CONTROL` remains WITHHELD.

Deferred/non-blocking: pressure overlay BD-006 and hosted HTML BD-007.

Authority: `VISUAL_SEMANTIC_ONLY`.
