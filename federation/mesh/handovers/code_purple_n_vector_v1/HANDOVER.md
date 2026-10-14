# CODE PURPLE — source-bound operator handover

**Checkpoint date:** 2026-10-14 UTC. Historical readback; refresh GitHub again at execution time. This handover deliberately corrects the stale values of the earlier delta ZIP.

## Control ownership and precedence

- [CODEX #1037](https://github.com/GBOGEB/CODEX/issues/1037): global CODE PURPLE orchestration, P0 first-red recovery; existing owner decisions prevail.
- [ABACUS #1929](https://github.com/GBOGEB/ABACUS/issues/1929): BD/LDAB joined error census and comparable evidence producer.
- [ABACUS #1860](https://github.com/GBOGEB/ABACUS/issues/1860): independent admission and unresolved review register.
- [CODEX #1041](https://github.com/GBOGEB/CODEX/pull/1041): existing Mycelium/MIP owner, now **merged**; its earlier exact-head failed CI remains a historical defect, and no repair for that cause is duplicated here.
- [CODEX #1042](https://github.com/GBOGEB/CODEX/pull/1042): existing branch-protection preflight owner, now **merged**. Do not create competing ruleset implementers.
- [ABACUS #1962](https://github.com/GBOGEB/ABACUS/pull/1962): temporal dashboard owner, now **merged**; the offline matrix here does not replace its native tests or gg_MATH.
- [ABACUS #1965](https://github.com/GBOGEB/ABACUS/pull/1965): bounded Ruff repair owner, **open at readback**, technical producer PASS for four-file measurement, independent admission unresolved.
- [ABACUS #1963](https://github.com/GBOGEB/ABACUS/pull/1963) and [#1964](https://github.com/GBOGEB/ABACUS/pull/1964): separate issue-burndown and DOW first-red owners; preserve their lease boundaries.

## Readback matrix — historical observations, NOT exact-current merge authority

| Object | Observed source SHA | Verified property | Unverified or blocked |
|---|---|---|---|
| CODEX main | `0569df2e4cb88c5802e11359d241167db97c3ca3` | GitHub default branch returned this SHA; `protected=false` | Current effective enforced admission; no ruleset-based protection evidence |
| ABACUS main | `85dad8fbdab530d40e6ccf2f664c455f89454aad` | GitHub branch reports `protected=true`; active ruleset #24494381 exists | `protection.enabled=false` in legacy protection subobject; effective operative rules/eligible review NOT independently accepted here |
| ABACUS #1965 | `c3f7d2f852139ea54c64b325cea44d1e5706f26e` | Native exact-head four-file Ruff `11→0`, 6 focused regressions PASS | Full native CI, RHEL8/9, security, independent review, root closure |
| CODEX #1041 historical PR head | `05f741e899dafbab44a40288c3863574c21d8f76` | 34 workflow successes, 3 failures; 3 canonical generator blob matches reconstructed | That head is now merged; do not credit that merge as governed approval |

The three generated Mycelium files from historical #1041 native diff had blobs `1791305de1ddf568c2132e61994a4c04c26605f9` (two mirrored inventories), `f5dae2f6f6e7021c88d856cd853088d3cc7c4c5f` (control). Prepared candidate commit [7779878](https://github.com/GBOGEB/CODEX/commit/777987869ded843261e3257fe57543083d94f15d) was **unattached at initial checkpoint** after branch update errors. Since #1041 later merged, confirm whether its contents are now integrated or still missing before any new source repair. No claim of new exact-main Mycelium producer DoV.

## Priority WBS / DoV sequence

| WBS | Existing owner | Required next evidence |
|---|---|---|
| C02 | CODEX #1041 / #1037 | Compare generated receipt bytes on current main; classify current Mycelium/stale first-red; preserve existing repair branch where possible |
| A02 | ABACUS #1965 | Preserve 11→0 scope receipt; obtain remaining exact-head CI/security, approvals and post-admission recurrence |
| A01/A03 | ABACUS #1964 / #1963 | Native terminal first-red census, artifact hashes and disjoint issue worker evidence |
| A05/E01 | ABACUS #1962 + gg_MATH | Native source-bound temporal producer, arbitrary N reindex, masked difference negatives, provider attestation |
| G01 | Repo owner/admin and eligible reviewer | Verify enforceable protected-main rules and required checks, complete independent review; no retrospective fabricated approval |

## Evidence policy

Each observation shall record `repository, source_sha, observed_at_utc, producer, workflow_run_id, attempt, job_id, artifact url/hash, tool/config/scope, unit, numerator/denominator, root_id, owner, result, admission_status`. UNKNOWN numeric values are JSON `null`. Record distinct finding occurrences, causal roots, reviews, and merge-authority states separately. Every changed SHA invalidates prior exact-head admission proof.

## Handover integrity limitations

The original `HANDOVER_V2.zip` is cited in issue [ABACUS #1929](https://github.com/GBOGEB/ABACUS/issues/1929) as a 29-file package containing 18 source attachments, but its raw bytes were not available for the migration comparison. This Git PR migrates the seven-file **N-vector recovery ZIP surface**, not the entire V2 package. The old recovery ZIP's manifest was inconsistent (it referenced `DROPIN_DELTA.md` absent from the recovery ZIP), and its JSON/model carried a stale 11→2 Ruff revision. Neither is silently overwritten as evidence: see issue history and the corrected immutable evidence anchors above.
