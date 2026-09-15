# DROP-IN CONTINUATION — ABACUS A10 / A9

Use this block to restart in a fresh chat without relying on prior conversation memory.

## Mission
Continue `GBOGEB/CODEX` from the exact-main A9 hosted-publication failure after PR `#733`.

Do **not** reopen A10 snapshot publication unless a concrete renderer defect appears. Do **not** create a second publication architecture or weaken hash/semantic/two-match predicates.

## Read first
1. current `main` ref;
2. `abacus_render_pipeline/A7_executable_semantic_runtime/data/governance_ledger.json`;
3. `abacus_render_pipeline/A7_executable_semantic_runtime/data/semantic_tuple_ledger.json`;
4. `abacus_render_pipeline/A10_snapshot_publication/handover/MIP_RECEIPT_2026-09-15.yaml`;
5. `abacus_render_pipeline/A10_snapshot_publication/handover/SESSION_HANDOVER_2026-09-15.md`;
6. this file;
7. `abacus_render_pipeline/A10_snapshot_publication/handover/SESSION_PROGRESS_LEDGER_2026-09-15.yaml`.

## Preserved authority
- PR `#729` merged as `6bb2f4c05468c9134bee1a7ae879d6c3977d7397` and admitted the repository-workflow Pages ownership MIP.
- Its exact-main A9 run `34927684226` failed before render on `semantic_boundary_preserved`.
- PR `#733` bound only the pointer/provenance meaning of that term and merged as `396ad4b17c86568cf749507e2b5198bcfe098429`.
- `DEBT-008 snapshot_receipt = CLOSED` and `TUP-0013` remain independently valid.
- `DEBT-007 multi_format_receipts = PARTIAL`.
- `TUP-0012 = active_stability_gate`.
- `TUP-0014 = active_validation_gate`.

## Exact-main result after PR #733
`ABACUS Multi-Format Publication` push run `34928083084` on exact source `396ad4b17c86568cf749507e2b5198bcfe098429` proved:

- candidate generation/parity/ownership/replay: PASS;
- `actions/deploy-pages`: PASS;
- hosted proof: FAIL CLOSED after 24 probes;
- governed candidate SHA: `6737e566b54b907cf54d53dd91160ccb4d09aba3e34fba2035a1bae0eb90214c`;
- hosted SHA: `39a754786ab9c2108d84d68fb29194901f5000032aea6d31f9326bf497acdefc`;
- semantic coverage: `0.0`;
- atomic decision: `WITHHOLD`.

Therefore **DEBT-007 is not closed**.

## Observed exact first-red — PAGES-SOURCE-MODE-001
The stale hosted SHA is exactly repository `docs/index.html` (2899 bytes).

GitHub's dynamic Pages publisher is still active outside repository workflow concurrency:

- dynamic run for `396ad4b...`: `34928079151`, cancelled/superseded;
- successor bot commit: `aebe86b4dc45376b1a8c3c438dbfee6f36d6d65d`;
- successor dynamic run: `34928104579`, PASS;
- build source: `./docs`;
- deploy target: `https://gbogeb.github.io/CODEX/`.

This proves the remaining ownership defect is GitHub Pages **legacy branch/Jekyll source mode (`main:/docs`)**, not A9 rendering, A10, or the repository `deploy-pages` workflow census. The dynamic publisher can overwrite the governed A9 artifact after A9 deploys.

## Bounded repair
Branch: `fix/a9-pages-source-mode-guard-20260915`.

The repair only:
- adds `scripts/check_pages_source_mode.py`;
- adds `tests/test_pages_source_mode.py`;
- runs source-mode classification tests on PRs;
- on exact-main push, fails A9 before rendering unless the Pages API reports `build_type: workflow`.

It does **not** change the publication carrier or proof thresholds and creates zero closure credit.

## Owner action — current and only external gate
In repository settings:

`Settings -> Pages -> Build and deployment -> Source -> GitHub Actions`

The GitHub connector cannot change this administration setting. Do not rerun the hosted proof while Pages remains in branch/Jekyll source mode.

## Re-entry sequence after owner action
Run exactly one normal exact-main A9 transaction and require:

```text
Pages build_type = workflow
-> candidate PASS
-> deploy-pages PASS
-> first hosted exact governed hash + semantic match
-> second consecutive exact hosted match
-> independent repeated convergence PASS
-> atomic PROMOTE
```

Only then perform one bounded closure writeback:
- `DEBT-007 = CLOSED`;
- `TUP-0012 = complete`;
- bind exact main SHA + Actions run + hosted receipt + artifact digest;
- preserve `DEBT-008 = CLOSED`;
- update handover/progress ledger;
- STOP.

If that exact-main proof fails, keep `DEBT-007 = PARTIAL` and recurse only on the newly observed first-red.
