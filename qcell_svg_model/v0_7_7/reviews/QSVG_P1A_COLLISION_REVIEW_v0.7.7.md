# QSVG-P1A collision / legibility review — v0.7.7

## Scope

Static coordinate review of the canonical MAIN layout introduced by QSVG-P1A. This is a bounded visual-control review, not engineering acceptance.

## Corrected result

`PASS_STRUCTURAL_AFTER_BOUNDED_REPAIR_WITH_AUTOMATED_CHECK_PENDING`

The first manual review overclaimed the absence of overlap. During P1B preparation a concrete conflict was found between:

- the `300→50 K conduction` annotation card; and
- the dotted-endpoint explanatory card.

The endpoint explanatory card has now been moved into the dedicated right-side flow/control column. This is a bounded collision repair, not a layout redesign.

## Reviewed regions after repair

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
| endpoint explanatory card | PASS_AFTER_REPAIR | moved to right-side column below flow legend |
| dotted endpoint guides | PASS_WITH_CROSSINGS | guide crossings are permitted; guides are conceptual, not piping geometry |
| temperature heat-map legend | PASS | dedicated bottom band |
| pressure legend | NOT_PRESENT | intentionally deferred |
| big teaching arrows | OFF | hidden by default and excluded from MAIN visual load |

## Codex review repairs incorporated

1. Right-to-left outer and inner parasitic paths now use reversed direction-specific gradients so start→end semantics remain red→orange and orange→blue respectively.
2. The nominal 50 K membrane now uses one authoritative 50 K colour (`#00e7c0`) rather than a spatial multi-temperature gradient.
3. A/B dark-blue legend cards now enforce white text through a CSS class with sufficient precedence.

## Non-regression findings

1. Flow no longer dominates the thermal body.
2. A/B/D/E identity remains visible without full-size arrows.
3. Dotted guides retain endpoint intent from the user-edited sheets.
4. Temperature remains the dominant colour semantics.
5. Pressure is not silently encoded with thermal colours.

## Remaining BD

`QSVG-BD-003` is **not fully closed in P1A** because automated collision checking belongs to P1B. P1B now contains an executable collision-box contract and CI gate.

Authority: `VISUAL_SEMANTIC_ONLY`.
