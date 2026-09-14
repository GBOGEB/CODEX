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
      HTML             PPTX             PDF            Markdown       Pages candidate
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
                              PREDEPLOY WITHHOLD
                                         |
                                         v
                            actions/deploy-pages@v4
                                         |
                                         v
                              real hosted Pages URL
                                         |
                            network fetch + SHA-256
                                         +
                              semantic parity replay
                                         |
                                         v
                            ONE atomic promotion
                       PROMOTE / WITHHOLD / REJECT
```

## Production carriers

A9 deliberately reuses `codex.contract_governance.builder.build_artifacts()` and the existing production `pptx_builder.py`, `pdf_builder.py`, and HTML template. It does not create a competing PPTX/PDF renderer stack.

The production builders return native telemetry while preserving their existing call contract for callers that ignore return values.

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

### Markdown

Markdown is generated deterministically from the same canonical workbook payload and is independently hash- and semantic-parity validated.

### GitHub Pages

The local Pages directory is only a **deployment candidate**. It does not itself prove publication.

The candidate `index.html` must be byte-identical to the governed HTML artifact. On `main`, GitHub Actions packages that candidate with `actions/upload-pages-artifact`, deploys it with `actions/deploy-pages`, then retrieves the actual hosted URL over the network. `hosted_pages_receipt.py` records the hosted bytes and semantic coverage. `receipt_validation.py` independently refetches the URL before the final atomic promotion receipt may reach `PROMOTE`.

This deliberately prevents an HTML directory or Pages upload artifact from being counted as hosted publication evidence.

## Cross-format parity

The execution receipt requires all five governed output candidates to preserve the same bounded canonical semantic token set:

- package identity;
- canonical content SHA-256;
- sheet identities;
- requirement identifiers.

Different file formats do not need byte identity. The Pages candidate is the exception because it is the deployment surface for the production HTML artifact, so its `index.html` must match the governed HTML bytes exactly.

## Receipt evidence

`receipts/multiformat_execution_receipt.json` carries the deterministic pre-deployment evidence: exact source commit, SSOT and tuple-ledger hashes, per-format artifact hashes, native telemetry, semantic parity, cross-format parity and replay result.

`receipts/github_pages_hosted_receipt.json` exists only after a real Pages deployment and records:

- exact source commit;
- Pages URL and final fetched URL;
- HTTP status;
- governed candidate hash;
- hosted response hash and byte count;
- semantic parity;
- deployment run ID;
- network fetch evidence.

`receipts/publication_promotion_receipt.json` issues one atomic decision:

- `WITHHOLD` when the deterministic multi-format bundle is valid but hosted Pages evidence is deliberately absent;
- `REJECT` when any governed artifact, replay, hosted receipt or independent hosted refetch is invalid;
- `PROMOTE` only when every format plus the real hosted Pages publication passes.

## Governance state

`DEBT-007 multi_format_receipts` remains **PARTIAL** until a `main` deployment produces a hosted Pages receipt and independent network revalidation reaches one atomic `PROMOTE`. Closure is a separate evidence-bound governance update; this implementation PR does not pre-close the debt.

`INV-008` makes the hosted-publication boundary explicit: a local Pages directory is not publication evidence.

## Authority boundary

Generated HTML/PPTX/PDF/Markdown/Pages outputs remain non-canonical derivatives. The SSOT and governed semantic ledgers remain authoritative.

Microsoft PowerPoint/Office365 host-native reflow remains outside the OpenXML structural receipt unless that host engine is separately executed and evidenced.

## Frontier after DEBT-007 closure

`DEBT-008 snapshot_receipt` remains open intentionally. Snapshot/image rendering should only join the contract after a real renderer supplies image-native evidence.
