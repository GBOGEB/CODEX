# Origin-independent temporal model — contract v1.1

Status: **offline reference, NOT a native or gg_MATH provider acceptance**. Canonical statistical/mathematical provider remains GBOGEB/gg_MATH; CODEX owns process coordination and ABACUS owns its own runtime evidence and admission.

## Two different clocks

- Revision/event index `j`: ordered observation linked to immutable repo, full source SHA, UTC, run/job/config and its source receipt.
- Logical recovery cycle `c`: causal root → bounded repair → replays → technical DoV → admission → recurrence control. One cycle can include many revisions; a single revision can affect several candidate cycles. Never identify `j` with `c`.
- An origin is an arbitrary integer `a`, so `k=j-a`. Rebase `j` by changing `a`, without changing source history or interval order. Old N−10 to new N implies old N+1 to new N+11, not a claim of elapsed time or completed repair.

## State and mask

For `m` revisions and `d` typed measurements, let `X∈(R∪{⊥})^(m×d)`. Every scalar is bound to `(repository, SHA, observed_at_utc, unit, producer, configuration digest, scope digest, denominator)`. An absent observation is `⊥`, serialized as JSON `null`, *never* `0`.

For `i=0,…,m−2`, use first-difference operator `D[i,i]=−1; D[i,i+1]=+1`, otherwise zero. `ΔX = D X` is only defined at **true** comparability mask entries `C[i,p]`; masked, absent, nonfinite or incomparable values emit `null`. Do not conflate a change in denominator, tool version, rules, scope, config, sampling time or provenance with repair gain. For ratio measures compare named compatible covered/eligible pairs; zero eligible changed lines is N/A.

A versioned root graph can use binary incidence `E[occurrence,root]`, `R[root,repair]`, `V[repair,replay]`. The product provides candidate paths, not confirmation of causality or authority to merge. A persistent causal root ID survives SHA changes and root splitting/merging preserves aliases.

## Native example (Ruff occurrence, not root closure)

For ABACUS PR #1965, `ruff==0.17.0` matched the identical four files at base `5ede8c97db4aba99fdcc44109e7230db69a3fd6b` and exact head `c3f7d2f852139ea54c64b325cea44d1e5706f26e`: before **11**, after **0**, opened **0**, resolved **11**, net **−11**, 100% bounded reduction. Producer [38590675476 / 115944391508](https://github.com/GBOGEB/ABACUS/actions/runs/38590675476), artifact `11906997311`, SHA-256 `fe241c5534a441e907d78c762a4a5758b4cf6a6fb3f8d68bac58ed5f910e6118`. Historical 11→2 evidence remains a previous revision, not the current four-file terminal measurement. Whole-repo Ruff, Bandit/Flake8, main coverage and root closure are UNKNOWN or different scope.

## Decisions

DoV and admission are conjunctive (exact-head verification AND required tests AND security AND eligible independent review AND effective branch protection AND applicable CI). If any gate is false/unknown, **HOLD**. Full PASS yields `ELIGIBLE_FOR_SEPARATE_OWNER_DECISION` rather than automatic merge.

DMAIC/W84 improvement requires comparable before/after receipts. `3P*` is a categorical process selector (`3PR`, `MIP`, `3PC`, `3P3`, `STOP`), not a numeric KPI. PCA is exploratory only when data permits; Bradley–Terry requires independent pairwise trials. No claim of modeled dynamics (`A_j,B_j`) follows from descriptive CI history.
