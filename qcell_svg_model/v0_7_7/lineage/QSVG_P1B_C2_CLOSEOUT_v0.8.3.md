# QSVG-P1B C2 visual-control closeout — v0.8.3

## Disposition

`C2_VISUAL_CONTROL = CLOSED_PASS_EXACT_HEAD_REPEAT`

This closeout is limited to visual-control semantics. It grants no engineering/SAT/OPEX/negotiation/release authority.

## BD contraction

- `QSVG-BD-003 text/annotation collision control` → **CLOSED_PASS_EXACT_HEAD_REPEAT**
- `QSVG-BD-004 layer-state control` → **CLOSED_PASS_EXACT_HEAD_REPEAT**

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
10. Review-derived thermal semantic guards added:
   - nominal 50 K shield must use a single authoritative 50 K colour;
   - right-to-left parasitic heat paths must use direction-correct reversed gradients;
   - A/B dark-card text contrast must be explicitly white.

## Exact-head runtime evidence

### Run A
- head: `280c17e0b5b9f57b775d2d7c0665c44444446a88`
- run: `34839673188`
- job: `103961455798`
- result: PASS

### Run B
- head: `86e31ba3b6cec24dca0dfee7e238818733be1a4a`
- run: `34839729228`
- job: `103961635886`
- result: PASS

### Run C — strengthened semantic checker
- head: `deabaaacd7cb4c103fab25ae84e402c74be6b27d`
- run: `34840022581`
- job: `103962561407`
- result: PASS

All observed runs completed the exact-SHA checkout, Python setup, and fail-closed QCELL visual-control step successfully.

## Remaining critical-path BD

The active core lane now contracts to **C3 PROOF_AND_REPEAT**, principally:

- `QSVG-BD-005` — clean YAML→SVG→HTML regeneration determinism: OPEN.
- `QSVG-BD-008` — typed visual receipt: implemented but should be promoted from draft to generator-bound canonical receipt during P1C.
- `QSVG-BD-009` — stable-artifact distinct-SHA repeat: CLOSED on P1A after review repair.

`QSVG-BD-010 CONTROL` remains WITHHELD until C3 closes.

## Deferred/non-blocking

- `QSVG-BD-006` pressure overlay.
- `QSVG-BD-007` hosted HTML path.

## Next frontier

`QSVG-P1C — deterministic SSOT regeneration + canonical receipt`.

Do not reopen MAIN geometry unless an observed review/runtime failure demands a bounded repair.
