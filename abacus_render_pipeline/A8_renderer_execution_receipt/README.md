# A8 — Renderer Execution Receipt

## Objective

Replace the synthetic `render_validation_passed=True` boundary with a real, content-addressed renderer execution receipt.

The A8 reference harness executes the governed renderer path:

`SSOT YAML -> theme runtime -> layout intelligence -> HTML artifact -> renderer checks -> semantic replay -> receipt -> promotion gate`

## Receipt Contract

Every execution receipt carries:

- artifact SHA-256;
- SSOT SHA-256;
- renderer version;
- theme;
- render mode;
- contrast result;
- layout result;
- overflow result;
- semantic replay result;
- tuple-ledger SHA-256;
- final accept/reject decision.

Generated outputs remain non-canonical derivatives. The receipt proves exactly which governed inputs and checks produced the promoted artifact.

## CI Evidence

The workflow generates, validates, and uploads:

- `reference_render.html` — actual rendered artifact;
- `renderer_execution_receipt.json` — machine-readable promotion evidence.

The same receipt is consumed by the A7 semantic acceptance gate; no boolean render override remains in the promotion path.
