# QCELL Sheet 4 Option B - Small-Flow Outcome

## Aim

Create a different outcome from the existing v0.8.1 canonical-lineage PR.

This branch is **not** intended to replace the existing branch. It explores an alternate visual strategy where sheet 4 becomes a lightweight, flow-readable teaching/diagnostic layer rather than the direct canonical MAIN merge.

## Design thesis

Use sheet 4 as an **overlay-first** interpretation:

- thermal shell remains the architectural base;
- flow arrows become small, local, and sparse;
- endpoint markers are retained only where they clarify causality;
- pressure/diagnostic information is kept in a separate optional layer;
- annotations are treated as toggled explanation, not always-on drawing content.

## Different outcome from existing branch

Existing branch aim:

> Canonical lineage integration using sheet 4 as the preferred refinement input.

Option B aim:

> Preserve sheet 4 as an alternate small-flow overlay experiment, with MAIN kept cleaner and less visually dense.

## Expected result

A cleaner viewer/teaching artifact where the operator can toggle:

1. base thermal architecture;
2. small flow direction hints;
3. endpoint/crossing guide marks;
4. pressure diagnostic overlays;
5. explanatory annotations.

## Non-goals

- Do not merge all sheet 4 details into MAIN immediately.
- Do not enlarge flow arrows.
- Do not flatten layers into one static SVG.
- Do not mix pressure colours into the thermal palette.

## Decision checkpoint

After generating Option B, compare against the canonical branch using:

- readability at full-page view;
- readability at zoomed component view;
- operator/teaching clarity;
- layer toggle usefulness;
- risk of visual clutter;
- ease of YAML SSOT conversion.
