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
                   repo-wide `pages` deployment boundary
                                         |
                            actions/deploy-pages@v4
                                         |
                                         v
                              real hosted Pages URL
                                         |
                       repeated exact-hash + semantic
                              hosted convergence
                                         |
                              independent repeat
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

The candidate `index.html` must be byte-identical to the governed HTML artifact. On `main`, GitHub Actions packages that candidate with `actions/upload-pages-artifact` and deploys it with `actions/deploy-pages` while holding the repository-wide `pages` concurrency group.

A deployment-success signal is also insufficient by itself. A9.3 treats the public endpoint as converged only after at least **two consecutive** network responses have all of:

- HTTP `200`;
- non-empty response bytes;
- exact SHA-256 equality with the governed Pages candidate;
- complete governed semantic-token parity.

`hosted_pages_receipt.py` records that convergence sequence. `receipt_validation.py` independently repeats the convergence check before the final atomic promotion receipt may reach `PROMOTE`.

This deliberately prevents an HTML directory, Pages upload artifact, deployment-success signal, or stale HTTP `200` response from being counted as hosted publication evidence.

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
- network fetch count;
- required consecutive match count;
- propagation observations leading to governed convergence.

`receipts/publication_promotion_receipt.json` issues one atomic decision:

- `WITHHOLD` when the deterministic multi-format bundle is valid but hosted Pages evidence is deliberately absent;
- `REJECT` when any governed artifact, replay, hosted receipt or independent hosted convergence check is invalid;
- `PROMOTE` only when every format plus the real hosted Pages publication passes.

## Governance state

`DEBT-007 multi_format_receipts` is **PARTIAL pending A9.3 stability re-proof**.

A valid historical hosted proof remains recorded for source `ed641574dedcf4f062ad333e07ef79d19388f3eb`, Actions run `34867675282`: real `deploy-pages`, hosted and governed SHA equality, semantic coverage `1.0`, independent refetch, final atomic `PROMOTE`.

A later exact-main burn-in, run `34868367167` for source `0f1d998165f601c116da166d694e3a69435ea8d2`, proved that `deploy-pages` success can precede public-endpoint convergence. The first hosted HTTP `200` returned SHA `39a754786ab9c2108d84d68fb29194901f5000032aea6d31f9326bf497acdefc` instead of governed candidate `6737e566b54b907cf54d53dd91160ccb4d09aba3e34fba2035a1bae0eb90214c`, with semantic coverage `0.0`. The receipt correctly rejected and atomic promotion did not run.

`A9_3_PAGES_STABILITY_REPAIR.md` defines the repair and exact-main re-close predicate. `INV-008` still requires real hosted evidence; `INV-009` additionally requires stable repeated convergence under the repository-wide Pages deployment boundary.

## Authority boundary

Generated HTML/PPTX/PDF/Markdown/Pages outputs remain non-canonical derivatives. The SSOT and governed semantic ledgers remain authoritative.

Microsoft PowerPoint/Office365 host-native reflow remains outside the OpenXML structural receipt unless that host engine is separately executed and evidenced.

## Next publication frontier

After stable exact-main A9.3 re-proof and evidence-bound re-closure of `DEBT-007`, `DEBT-008 snapshot_receipt` remains the next generic publication frontier. Snapshot/image rendering should only join the contract after a real renderer supplies image-native evidence.
