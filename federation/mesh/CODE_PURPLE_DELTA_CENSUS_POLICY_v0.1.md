# CODE PURPLE — sparse temporal census (post #984)

Status: **draft follow-up / instrumentation candidate**. This is a child of [CODEX PR #984](https://github.com/GBOGEB/CODEX/pull/984), not a repair to its already-merged head, not a competing SSOT, and not an admitted security-control replacement.

## Observed baseline and facts

The machine-readable evidence baseline is [CODE_PURPLE_PR984_POSTMERGE_CENSUS_20261012.json](CODE_PURPLE_PR984_POSTMERGE_CENSUS_20261012.json).

- First seed snapshot: 49 check entries, 2 observed successes, terminality missing.
- User's merge-dialog snapshot: 54 successes, 3 failing, one cancellation, one skip reported on screen; 4 "not successful" entries are not necessarily four failed code defects.
- Final exact PR head `90e3396a...`: **65 check entries = 55 success + 4 failure + 1 cancelled + 5 skipped**. Two failures correspond to separate W003 governance-gate workflow runs with the same PR-007 header root; each had `run_attempt=1`. The Agentic scan cancellation was followed by a separate successful run, not a retry attempt.
- Merge commit `768c9e35...`: 47 check entries, 38 success, 2 failures, 3 cancelled, 4 skipped. These are **a different execution population**; do not subtract merge counts from PR-head counts as if they were one stable test suite.
- A later CODEX `main@0239f24c...`: 3 successful Pages-related jobs in the inspected result, not a full-main CI verdict.
- PR #984 has **12 commits** and one recorded merge. This is **not** proof of 12 independent `.self` iterations; distinct execution/feedback/re-entry cycles still need separate bound receipts.

## Incremental data contract

`scripts/code_purple_census_delta.py` implements the first safe, **read-only delta layer**. Every observation has a governed identity (repo + scope + exact commit SHA) and a stable record ID (e.g. `check-run:<check-run-id>` or `workflow-run:<run-id>:attempt:<n>`). Input is a sanitized projection, **not raw GitHub logs**.

```text
previous validated semantic state
  + current validated semantic state
  -> canonical SHA-256
  -> added records + removed IDs + changed fields only
  -> delta receipt (previous + next identity and content digests)
  -> replay to assert exact next content identity
  -> NO_CHANGE: publish nothing
  -> DELTA_READY: stage the small delta for the existing CODEX single Pages writer
```

- First publication needs an **explicit, full baseline** with a content SHA; a missing previous state is HOLD, not an assumed empty census.
- Subsequent updates contain only semantic differences. If the only change is observation time, no delta is emitted.
- A changed commit is **CROSS_HEAD_REBASELINE** and never an inferred improvement.
- Any stale previous hash, changed scope, unexpected/raw-log field, conflicting ID, invalid SHA or corrupt replay is fail-closed.
- No direct Git push, PR merge, owner-attestation, secret read, automated re-run or engineering acceptance is performed by the emitter.
- **Transport caveat:** GitHub Pages currently stages/uploads a complete site artifact on deployment. The payload can be delta-only, but claiming GitHub Pages itself performs binary/HTTP incremental patch deployment would be inaccurate. Consumers need to retain the last accepted baseline/delta chain; a periodic checkpoint/compaction policy will be necessary after an evidence-bound retention limit.
- This PR intentionally **does not change** the existing `.github/workflows/pages.yml` or create a second Pages writer. Integrating the emitter into its existing runtime is a separate exact-head gate once the previous published baseline/receipt can be obtained and independently verified.

### CLI

```sh
python scripts/code_purple_census_delta.py \
  --previous /tmp/code-purple-prev.json \
  --current /tmp/code-purple-next.json \
  --output /tmp/code-purple-change-only.json
python -m unittest discover -s tests -p 'test_code_purple_census_delta.py'
```

It refuses absent inputs. It validates deterministic replay before writing a changed delta; `NO_CHANGE` does not touch the output. The tests cover red/green status transitions as record field deltas, snapshot timestamp-only no-op, added/removed records, changed commit baseline, duplicate or unexpected fields and replay corruption.

## Mission control and statistical adequacy

The semantic census is **not** a KPI, PCA or Bradley–Terry result. Connect it to existing `mission_control/mycelium/` source observations, `scripts/build_missioncontrol_metrics.py` and GLOB only after the measured denominator and provenance are settled.

Track separately:

| Dimension | Valid meaning |
|---|---|
| Number of PR commits | Git history; does not count process improvements |
| Workflow runs / run attempts | Native execution identity; distinguish a *new run* from `run_attempt > 1` |
| Check entries / test cases | Check-run entries are **not** individual test cases; test case count is unknown without structured test reports |
| Unique first-red signatures | Repair roots after deduplication by failure family and attributable context |
| Closed PRs | Delivery state only; not Code Purple global DoV |
| Iterations | Independent `input → process → evidence → update → proof` cycles, not repeated snapshots |
| Global DoV | Governed mission exit criteria only, including accepted consumer proof if required |

For statistically defensible analytical views, require a declared **population**, stable denominator and independent, comparable observations. As a conservative starting point, withhold confirmatory PCA/BT claims until there are at least 20–30 independent, sufficiently complete iterations (more for many PCA features), measurable variance, and adequately connected observed pairwise comparisons for BT. CODEX's existing PCA routine has a lower **computational feasibility** threshold (3 complete observations and 2 numeric features), not a guarantee of inferential confidence. Source status, independence and sampling bias can still withhold analysis even at higher N.

## Next admissible action

1. Run the new deterministic replay unit tests against the PR head.
2. Bind its exact-head CI and review; quarantine unrelated/red inherited checks with evidence, not with suppressed gates.
3. Bootstrap one sanitized, hash-bound current state through the existing CODEX publisher.
4. On subsequent publication events generate only content deltas, stage them with the **one canonical Pages writer**, and verify consumer replay/readback.
5. After one independent ABACUS consumer proves the payload, propose DOW/REX reuse; leave QPS engineering acceptance with its child authority.

`authority_transfer=false`; `formal_credit_delta=0`; `engineering_credit_delta=0`.
