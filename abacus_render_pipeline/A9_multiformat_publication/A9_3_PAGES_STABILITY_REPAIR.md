# A9.3 GitHub Pages Stability Repair

## State

`DEBT-007 multi_format_receipts = PARTIAL_PENDING_STABILITY_REPROOF`

A9.2 closed the debt from a real exact-main hosted publication proof. That proof remains valid historical evidence. A later exact-main burn-in exposed a separate repeatability defect, so current governance reopens the debt rather than allowing an earlier success to compensate for a newer failure.

A10 snapshot proof remains independently valid and `DEBT-008 snapshot_receipt` remains CLOSED. This repair does not unwind A10 image-native evidence.

## Valid proof retained

The earlier hosted proof remains valid:

- exact source SHA: `ed641574dedcf4f062ad333e07ef79d19388f3eb`;
- Actions run: `34867675282`;
- real `deploy-pages` execution: PASS;
- hosted HTTP: `200`;
- governed/hosted SHA-256 equality: PASS;
- semantic coverage: `1.0`;
- independent hosted refetch: PASS;
- final atomic decision: `PROMOTE`.

A9.3 does not erase or reinterpret that evidence.

## Regression / first red

Post-closure exact-main run `34868367167`, source SHA `0f1d998165f601c116da166d694e3a69435ea8d2`, produced a stronger burn-in test.

The deterministic candidate job passed. The real Pages deployment also reported success. The first hosted network observation then returned HTTP `200` but did not contain the governed artifact:

| Signal | Governed candidate | Hosted observation |
| --- | --- | --- |
| SHA-256 | `6737e566b54b907cf54d53dd91160ccb4d09aba3e34fba2035a1bae0eb90214c` | `39a754786ab9c2108d84d68fb29194901f5000032aea6d31f9326bf497acdefc` |
| Hosted bytes | governed candidate | `2899` |
| Semantic coverage | `1.0` required | `0.0` |
| Required semantic tokens | 8 | 0 present |
| Hosted receipt | `accept` required | `reject` |

The atomic promotion step was skipped. This is correct fail-closed behavior.

The proven defect is therefore not deterministic Markdown, PPTX/PDF generation, local candidate parity, snapshot rendering, or receipt tamper resistance. The defect is that a successful Pages deployment signal does not guarantee the public endpoint has already converged to the governed bytes at the first HTTP `200` observation.

The repository also contains multiple Pages deployment workflows. Several use the repository-wide `pages` concurrency group, while the original A9.1 job used a separate `abacus-pages-production` group. A9.3 removes that avoidable coordination gap. It does not claim concurrency was the sole cause of the observed stale response; propagation latency remains independently possible.

## Repair

A9.3 adds two non-compensating controls.

### 1. Repository-wide deployment serialization

The A9 hosted deployment/proof job now holds the same `pages` concurrency boundary used by the repository's canonical Pages workflows.

That boundary is held across:

`deploy-pages -> hosted convergence receipt -> independent hosted convergence -> atomic promotion`

A separately configured/manual workflow that does not share the group can still collide. Such a collision remains fail-closed because hosted bytes must match the governed digest and semantic token set.

### 2. Stable hosted convergence, not first-200 acceptance

`hosted_pages_receipt.py` no longer treats the first HTTP `200` as the final hosted state.

It polls the public Pages URL until it observes at least **two consecutive** responses satisfying all of:

- HTTP `200`;
- non-empty body;
- exact SHA-256 equality with the governed Pages candidate;
- complete governed semantic-token parity.

The receipt records propagation observations and the number of attempts. Exhaustion rejects rather than degrading the predicate.

`receipt_validation.py` then performs an independent second convergence sequence, again requiring at least two consecutive exact governed responses before atomic promotion can reach `PROMOTE`.

## New invariant

`INV-010`:

> A GitHub Pages deployment-success signal is not sufficient hosted evidence: promotion requires at least two consecutive exact governed hosted responses while holding the repository-wide Pages deployment concurrency boundary, followed by an independent repeat of that convergence check.

`INV-009` remains owned by the already-merged A10 snapshot receipt and is not repurposed.

## Re-close predicate

Do not re-close `DEBT-007` from this implementation branch.

Re-closure requires a new exact-main run under A9.3 that proves:

1. deterministic HTML/PPTX/PDF/Markdown/Pages candidates accepted;
2. cross-format parity passed;
3. Pages deployment completed;
4. hosted receipt reached two consecutive exact governed matches;
5. independent validation reached its own two consecutive exact governed matches;
6. exact hosted hash equals governed candidate hash;
7. semantic coverage is `1.0`;
8. final atomic promotion receipt is `PROMOTE`.

Only a separate evidence-binding governance update may then return `DEBT-007` to `CLOSED` and `TUP-0012` to complete.

## Authority boundary

This repair changes publication-evidence stability only. It does not create:

- Microsoft PowerPoint or Office365 host-native reflow proof;
- new snapshot/image authority beyond A10's existing bounded proof;
- QPS engineering acceptance;
- safety, compliance, procurement, negotiation, release, or project acceptance authority.

After A9 stable re-closure, do not reopen A10/`DEBT-008` without a concrete snapshot-renderer defect. Remaining generic improvement should proceed through still-open debts or a newly evidenced frontier rather than inventing another publication abstraction.
