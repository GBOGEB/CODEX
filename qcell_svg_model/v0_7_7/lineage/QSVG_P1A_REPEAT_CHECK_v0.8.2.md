# QSVG-P1A distinct-SHA repeat check — v0.8.2

## Repeat A

Branch head before this marker: `a381d0c005defe71e4bf8256c2af336e199dd56b`.

Observed stable content blobs:

- SSOT YAML: `eb11498604af72c73b8863c09958b55e78a33b84`
- canonical SVG: `a5ae9a756b2920bbf68f79647b602af37f1ee68d`
- interactive HTML: `7a014cea26b0603c26b7e990118df41fca29f046`

This marker intentionally changes only lineage metadata. The next observation must occur at the new distinct branch head and confirm the same three artifact blob SHAs.

Interpretation rules:

- identical blobs across distinct commit SHAs proves **artifact stability across a non-rendering lineage commit**;
- it does **not** prove YAML→SVG→HTML generator determinism;
- therefore QSVG-BD-009 may close to `PASS_STABLE_ARTIFACT_REPEAT` if Repeat B matches;
- QSVG-BD-005 remains open until an actual regeneration workflow reproduces the same normalized artefacts.

Authority remains `VISUAL_SEMANTIC_ONLY`.
