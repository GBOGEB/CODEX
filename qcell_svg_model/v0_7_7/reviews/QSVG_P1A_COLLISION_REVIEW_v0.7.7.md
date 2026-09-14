# QSVG-P1A collision / legibility review — v0.7.7

## Scope

Static coordinate review of the canonical MAIN layout introduced by QSVG-P1A. This is a bounded visual-control review, not engineering acceptance.

## Result

`PASS_STRUCTURAL_WITH_AUTOMATED_COLLISION_CHECK_PENDING`

## Reviewed regions

| Region | Result | Note |
|---|---|---|
| 300 K membrane labels | PASS | top-left reserved text area |
| vacuum 300→50 label | PASS | inside outer vacuum region |
| 50 K shield labels | PASS | above 2 K mass; no flow legend overlap |
| 2 K mass labels | PASS | centered within protected core |
| parasitic outer-left label | PASS | separate card fill used |
| parasitic outer-right label | PASS | separate card fill used |
| parasitic inner-right label | PASS | placed clear of 2 K mass |
| parasitic inner-left label | PASS | placed below left inner path |
| compact A/B/D/E legend | PASS | isolated right-side region |
| dotted endpoint guides | PASS_WITH_CROSSINGS | guide crossings are permitted; guides are conceptual, not piping geometry |
| temperature heat-map legend | PASS | dedicated bottom band |
| pressure legend | NOT_PRESENT | intentionally deferred |
| big teaching arrows | OFF | hidden by default and excluded from MAIN visual load |

## Non-regression findings

1. Flow no longer dominates the thermal body.
2. A/B/D/E identity remains visible without full-size arrows.
3. Dotted guides retain endpoint intent from the user-edited sheets.
4. Temperature remains the dominant colour semantics.
5. Pressure is not silently encoded with thermal colours.

## Remaining BD

`QSVG-BD-003` is **not fully closed** because this review is coordinate/static and not yet an automated text-box collision scan.

Closure predicate:
- automated or deterministic geometry check over annotation/card bounding boxes;
- zero forbidden text-card overlaps in all default presets;
- any intentional guide crossing explicitly allow-listed.

Authority: `VISUAL_SEMANTIC_ONLY`.
