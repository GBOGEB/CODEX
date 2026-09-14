# QSVG-P1A post-review distinct-SHA repeat — v0.8.3

## Result

`PASS_STABLE_ARTIFACT_REPEAT_AFTER_REVIEW_REPAIR`

The review-repaired canonical MAIN artifact was observed unchanged across distinct branch heads:

- repair artifact head: `72a7688da2047adee2a8de4b18de6df16e5c07b2`
- later receipt/lineage head: `6cde6609b9af4e42d191d1a3969a6f62dc50e2e2`

Stable canonical content blobs:

- SSOT YAML: `eb11498604af72c73b8863c09958b55e78a33b84`
- canonical SVG: `02f5572749e3997f8f23a87a4aa48c4af9d0e752`
- interactive HTML: `7a014cea26b0603c26b7e990118df41fca29f046`

## Review repairs contained in repeated SVG

- direction-specific reversed gradients on right-to-left outer/inner parasitic paths;
- nominal 50 K membrane mapped to the single authoritative 50 K colour `#00e7c0`;
- A/B legend text contrast enforced in CSS;
- endpoint explanatory card moved out of the conduction annotation region.

## BD effect

`QSVG-BD-009` is again **CLOSED_PASS_STABLE_ARTIFACT_REPEAT** after the review repair.

`QSVG-BD-005` remains **OPEN**: persistence across commit SHAs is not the same as clean YAML→SVG→HTML regeneration.

Authority remains `VISUAL_SEMANTIC_ONLY`.
