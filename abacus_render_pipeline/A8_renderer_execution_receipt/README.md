# A8 — Renderer Execution Receipts

## Objective

Replace synthetic renderer-validation booleans with content-addressed execution evidence and extend the same governance contract horizontally across production publication formats.

Generated outputs remain non-canonical derivatives. MASTER YAML and governed registries remain authoritative.

## A8.0 reference path

The retained reference harness executes:

`SSOT YAML -> theme runtime -> layout intelligence -> HTML artifact -> renderer checks -> semantic replay -> receipt -> promotion gate`

The reference receipt proves the original governance loop and remains a compatibility/control surface.

## A8.2 production multi-format path

A8.2 adds the first production horizontal expansion without creating a new authority layer:

`same SSOT -> native PPTX renderer + native PDF renderer -> per-renderer telemetry -> independently revalidated hashes/content -> cross-format parity -> ONE bundle promotion receipt`

Required production formats in this pulse:

1. PPTX
2. PDF

Markdown and GitHub Pages remain the next DEBT-007 expansion stage.

### PPTX native telemetry

The PPTX path uses `python-pptx`, then re-opens the generated OpenXML package and records:

- slide count and native slide dimensions;
- shape-boundary violations;
- content-box overlap count;
- font-size / text-box-height margin;
- extracted content lines;
- deterministic package normalization for repeatable SHA-256.

Important boundary: this is native OpenXML structure plus renderer font geometry. It does **not** claim that the Microsoft PowerPoint host layout engine has been executed. That host-native reflow proof remains a possible later hardening step rather than being silently inferred.

### PDF native telemetry

The PDF path uses ReportLab and validates the resulting PDF with `pypdf`. It records:

- page count and exact page dimensions;
- ReportLab-native text width measurements;
- minimum available width margin;
- extracted content lines.

### Cross-format parity

The same SSOT-derived content fingerprint must be recovered independently from PPTX and PDF. Any content, layout, overflow, parsing, lineage or parity failure rejects the full bundle.

## Receipt contracts

### Reference HTML

`renderer_execution_receipt.json` carries:

- artifact SHA-256;
- SSOT SHA-256;
- renderer version;
- theme and render mode;
- contrast/layout/overflow/replay checks;
- tuple-ledger SHA-256;
- accept/reject decision.

### Production PPTX/PDF bundle

`multiformat_execution_receipt.json` carries:

- one SSOT SHA-256 and tuple-ledger SHA-256;
- exact required format set `[pptx, pdf]`;
- one content-addressed artifact record per format;
- renderer-native telemetry and checks per format;
- independently comparable content fingerprints;
- cross-format parity result;
- semantic replay result;
- one bundle accept/reject decision.

`multiformat_promotion_receipt.json` is the single production promotion receipt for the required format set. Promotion requires independent revalidation of both artifacts, parity, replay and closed-loop governance state.

## CI evidence

`ABACUS Semantic Runtime` generates, validates and uploads:

- `reference_render.html`;
- `renderer_execution_receipt.json`;
- legacy/reference `promotion_receipt.json`;
- `production_render.pptx`;
- `production_render.pdf`;
- `multiformat_execution_receipt.json`;
- `multiformat_promotion_receipt.json`.

## Governance state

- `TUP-0011` — content-addressed renderer execution receipt frontier.
- `TUP-0012` — production PPTX/PDF multi-format receipt bundle and single promotion receipt.
- `INV-006` — promotion requires independently revalidated content-addressed receipt evidence.
- `INV-007` — multi-format promotion is atomic: all required formats and cross-format parity must pass together.
- `DEBT-006 renderer_binding` — CLOSED.
- `DEBT-007 multi_format_receipts` — PARTIAL: PPTX/PDF bound; Markdown/GitHub Pages remain.
