# Disjoint execution pulse — 2026-10-13

Status: STAGED / NON-AUTHORITATIVE. No automatic crew dispatch, merge approval, or engineering-credit promotion.

## One writer, six disjoint lanes

| Lane | File/process ownership | Target | Verification requirement |
|---|---|---|---|
| A Quality | `scripts/verify_disjoint_census.py`, `scripts/collect_disjoint_evidence.py`, relevant tests | 9/9 populations explicitly MEASURED or WITHHELD; >=1 real code-coverage ratio | Real coverage.xml; exact SHA, run, positive denominator and artifact digest |
| B UBI 9 | `.github/workflows/disjoint-census-runtime.yml` | Maintain two successful jobs, output bytes+SHA-256 | Completed exact-head run, UBI image identity and output artifact |
| C LDAB | existing LDAB probes, no shared modifications with B | One actual debugger session, steps>0 | Container ID, image digest, loopback listener, debugger transcript and logs |
| D Crew | read-only MissionControl control-plane observations | Actual dispatch/return identities; queue/latency/throughput | Authenticated receipts, queue snapshot, worker leases and timestamp anchors |
| E Dashboard | `docs/missioncontrol_disjoint_evidence.html` and existing single Pages writer | N to N+1 metrics readable, unknown != zero | Verified consumed source JSON digest, browser/current readback |
| G Governor | settings, reviews, admission | effective protection and independent review | Human approval plus server-side readback |

These represent **work partitions**, not a claim that five authenticated workers are running. Control manifest still defaults mutation to disabled; do not bypass.

## Measured historical anchors — distinct populations

- Original CODEX executable registration: 30/457 = 6.5646%; later 30/460 = 6.5217%; difference **-0.0429 percentage points** because denominator increased by 3. Registered asset count remains 30.
- CODEX isolated census/UBI 9 [run 38411427222](https://github.com/GBOGEB/CODEX/actions/runs/38411427222): **2 successful jobs / 2 total** at head `884e6a70e3de2b94a9fa2f876ce18ba1b87418d9`. Not statement coverage, not an LDAB session, not engineering acceptance.
- Actual live Ruff/Pyright eligible files, statement/branch/diff coverage, LDAB sessions, crew queue/wait/utilization, BD net burn: **UNKNOWN** pending exact-head receipts.

## Every N pulse must provide

`repo, head_sha, run_id, source_artifact_sha256, timestamp, population_id, numerator_N, denominator_N, numerator_N1, denominator_N1, delta_numerator, delta_denominator, delta_percentage_points, source_status, review_status`.

For each valid comparable population: `delta_pp=100*(numerator_N1/denominator_N1 - numerator_N/denominator_N)`. If either denominator is zero/missing or either source is unverified, `delta_pp=null`. A changed denominator must be shown independently. BD defects, workflow runs, REX signatures, and PR counts are **different units**.

## Release boundary

DOD (implemented/tested locally) is different from DOV (exact-head CI/runtime/reviewer/consumer acceptance). No publication through a second Pages writer; no main push or new PR as part of this pulse.
