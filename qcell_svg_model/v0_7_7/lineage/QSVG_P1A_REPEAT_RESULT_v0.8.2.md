# QSVG-P1A distinct-SHA repeat result — v0.8.2

## Result

`PASS_STABLE_ARTIFACT_REPEAT`

Two distinct branch heads were observed:

- Repeat A head: `a381d0c005defe71e4bf8256c2af336e199dd56b`
- Repeat B head: `cc42cb2fdb9f8246642a023d4858337bc6a90212`

The three canonical content blobs remained identical at Repeat B:

| Artifact | Repeat A blob | Repeat B blob | Result |
|---|---|---|---|
| SSOT YAML | `eb11498604af72c73b8863c09958b55e78a33b84` | `eb11498604af72c73b8863c09958b55e78a33b84` | PASS |
| canonical SVG | `a5ae9a756b2920bbf68f79647b602af37f1ee68d` | `a5ae9a756b2920bbf68f79647b602af37f1ee68d` | PASS |
| interactive HTML | `7a014cea26b0603c26b7e990118df41fca29f046` | `7a014cea26b0603c26b7e990118df41fca29f046` | PASS |

## BD effect

- `QSVG-BD-009` → **CLOSED_PASS_STABLE_ARTIFACT_REPEAT**.
- `QSVG-BD-005` → remains **OPEN** because this proves persistence/stability, not clean regeneration from SSOT.

## Important boundary

No claim is made that YAML has yet regenerated SVG/HTML bit-for-bit. That requires a generator execution and normalized-output comparison in P1C.

Authority remains `VISUAL_SEMANTIC_ONLY`; no engineering/SAT/OPEX/negotiation/release credit is created.
