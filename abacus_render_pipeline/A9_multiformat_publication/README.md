# A9 — Receipt-Governed Multi-Format Publication

A9 expands the A8 content-addressed renderer receipt horizontally across production publication formats without adding another semantic authority layer.

## Governed loop

```text
Contract Governance SSOT
        |
        v
canonical workbook payload + content hash
        |
        +----------------+----------------+----------------+----------------+
        |                |                |                |                |
        v                v                v                v                v
      HTML             PPTX             PDF            Markdown       GitHub Pages
        |                |                |                |                |
        |       python-pptx native        |                |                |
        |       geometry/row telemetry    |                |                |
        |                                 |                |                |
        |                       ReportLab flowable          |                |
        |                       placement telemetry        |                |
        +----------------+----------------+----------------+----------------+
                                         |
                                         v
                              cross-format semantic parity
                                         +
                                artifact SHA-256 binding
                                         +
                                  semantic delta replay
                                         |
                                         v
                          multi-format execution receipt
                                         |
                             independent hash validation
                                         |
                                         v
                            ONE publication promotion
                              receipt: PROMOTE/REJECT
```

## Production carriers

A9 deliberately reuses `codex.contract_governance.builder.build_artifacts()` and the existing production `pptx_builder.py`, `pdf_builder.py`, and HTML template. It does not create a competing PPTX/PDF renderer stack.

The production builders now return native telemetry while preserving their existing call contract for callers that ignore return values.

### PPTX native telemetry

- slide count;
- table-slide count;
- rendered row count;
- maximum rows per table;
- shape count;
- slide-bound geometry violations;
- layout and overflow result.

### PDF native telemetry

- ReportLab layout-engine completion;
- rendered page count;
- table/row/flowable counts;
- page dimensions;
- post-build empty-page count;
- overflow result based on successful native flowable placement without `LayoutError`.

## Cross-format parity

The A9 receipt requires all five governed outputs to preserve the same bounded canonical semantic token set:

- package identity;
- canonical content SHA-256;
- sheet identities;
- requirement identifiers.

This proves source-content preservation across renderers without pretending that byte-identical artifacts are required across different file formats.

GitHub Pages is intentionally a deployment surface for the production HTML artifact. Its `index.html` must therefore be byte-identical to the governed HTML artifact.

## Receipt evidence

`receipts/multiformat_execution_receipt.json` carries:

- exact source commit;
- SSOT SHA-256;
- canonical content SHA-256;
- tuple-ledger SHA-256;
- per-format artifact SHA-256;
- per-format renderer version;
- per-format native telemetry;
- per-format semantic parity;
- cross-format parity;
- semantic replay result;
- accept/reject decision.

`receipts/publication_promotion_receipt.json` independently validates that evidence and issues one `PROMOTE` or `REJECT` decision bound to all required artifacts.

## Authority boundary

Generated HTML/PPTX/PDF/Markdown/Pages outputs remain non-canonical derivatives. The SSOT and governed semantic ledgers remain authoritative.

## Remaining frontier

`DEBT-008 snapshot_receipt` remains open intentionally. The next expansion should bind snapshot/immersive image rendering to the same A9 receipt contract using image-native telemetry rather than claiming snapshot coverage without a real renderer execution.
