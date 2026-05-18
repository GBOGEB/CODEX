# PR Notes - QCELL SVG Model v0.8.1

## Purpose

Add the QCELL full engineering + coding handover package and preserve the provided Draw.io artifact as canonical lineage input.

## Key updates

- Adds v0.8.1 handover files under `qcell_svg_model/v0_8_1/`.
- Adds `QCELL_PARASITIC.drawio.svg` with four embedded Draw.io sheets.
- Adds sheet review focusing on sheet 4: `Copy of Copy of Copy of BSLN_0`.
- Records rule: flow arrows/details must remain visually smaller and layer-separated.
- Keeps pressure diagnostic palette separate from thermal/temperature palette.

## Immediate next implementation target

Build v0.7.7/v0.8.1 canonical MAIN merge using:

1. Sheet 2 grouping lessons.
2. Sheet 3 small legend/arrow lessons.
3. Sheet 4 endpoint/layer separation lessons.
4. YAML SSOT generation path for repeatable SVG/HTML output.

## Non-regression guardrails

- Do not let flow arrows dominate MAIN.
- Do not mix pressure colours into thermal palette.
- Preserve layer toggling/muting behaviour.
- Preserve central 2 K mass readability.
- Treat Draw.io as lineage/input, not as final CAD truth.
