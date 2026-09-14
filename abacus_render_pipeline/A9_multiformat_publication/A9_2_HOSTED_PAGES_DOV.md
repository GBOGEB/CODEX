# A9.2 Hosted GitHub Pages DoV — DEBT-007 Closure

## Closure decision

`DEBT-007 multi_format_receipts = CLOSED`

This closure is based on hosted publication evidence from the exact `main` source commit below. It is not inferred from a local HTML directory, upload artifact, merge event, or pre-deployment candidate receipt.

## Exact evidence

| Evidence | Value |
| --- | --- |
| Source commit | `ed641574dedcf4f062ad333e07ef79d19388f3eb` |
| GitHub Actions run | `34867675282` |
| Hosted URL | `https://gbogeb.github.io/CODEX/` |
| Hosted HTTP status | `200` |
| Publication ID | `ABACUS-CGW-W000-W001` |
| Hosted / governed Pages SHA-256 | `6737e566b54b907cf54d53dd91160ccb4d09aba3e34fba2035a1bae0eb90214c` |
| Hosted bytes | `2516` |
| Hosted semantic parity | `PASS` |
| Semantic coverage | `1.0` (`8/8` tokens) |
| Hosted receipt SHA-256 | `276d1e9b5e51d5fbe9bd9ec9c441b9917efafc5d87dc98cf1d672b26bdbbdcc9` |
| Promotion receipt SHA-256 | `aa30526e6c878a5b81942a72499da381727126c043114ba16e8561ba187f5834` |
| Workflow proof artifact digest | `sha256:a6fb8a2b821d61da90ea556bc1680d969415ad3e389a007a3af6589f928495db` |
| Final atomic decision | `PROMOTE` |

## Multi-format receipt set

The final promotion receipt accepted every required carrier and recorded these artifact hashes:

| Format | SHA-256 |
| --- | --- |
| HTML | `6737e566b54b907cf54d53dd91160ccb4d09aba3e34fba2035a1bae0eb90214c` |
| GitHub Pages | `6737e566b54b907cf54d53dd91160ccb4d09aba3e34fba2035a1bae0eb90214c` |
| Markdown | `e02e7b5865fd8106540865df0061074190aae7a56c96d80ceb1784ff3592058a` |
| PPTX | `8312384732e25c0a1953a8d463e947dfe2774b08694c0c9e6729a7becb9d707b` |
| PDF | `fce5b274f529975b170e2d914ec20deabe06bd6d25f356959adeaadef1cbceb6` |

Canonical content SHA-256:

`4b3417239e11b0b57b091310430d2dd7ae3288c5d6e8d9055780e6d92cca2259`

SSOT SHA-256:

`ecb60d03180ec3514ea4e3f1a62c1fad2ce1fabee55dfe010e94451cfc2d5bb5`

## Required predicates and result

The final promotion receipt recorded all of the following as `true`:

- multi-format execution receipt valid;
- multi-format execution accepted;
- all format receipts accepted;
- cross-format parity passed;
- GitHub Pages hosted receipt present;
- GitHub Pages hosted receipt valid;
- hosted hash and semantic parity independently revalidated;
- reconstruction/DAG completeness passed;
- semantic delta replay passed;
- replay ready.

The hosted receipt itself recorded:

- `decision: accept`;
- `fetch_method: network_get_after_actions_deploy_pages`;
- exact local artifact SHA-256 equal to hosted SHA-256;
- semantic coverage `1.0` with no missing tokens.

The final promotion stage then performed the separately required network refetch and completed successfully, producing `decision: PROMOTE`.

## Non-compensating boundary

This evidence closes the generic multi-format publication receipt debt only.

It does **not** claim:

- Microsoft PowerPoint / Office365 host-native reflow proof;
- snapshot/image receipt proof;
- QPS engineering acceptance;
- safety, compliance, procurement, negotiation, or project acceptance authority.

Generated publication artifacts remain non-canonical derivatives. The governed SSOT and semantic ledgers remain authoritative.

## Next publication frontier

`DEBT-008 snapshot_receipt` remains separate and open. A real rendered-image/snapshot path must obtain its own renderer-native receipt before snapshot evidence can be promoted.
