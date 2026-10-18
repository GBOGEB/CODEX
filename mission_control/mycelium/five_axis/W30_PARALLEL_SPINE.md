# CODE PURPLE W30 — Parallel DAG / SIPOC / SPINE fan-in

**Source-owned CODEX read-only adapter, not a replacement for existing ABACUS and CODEX control authorities.** Source of truth stays in owner repos, exact-head native CI, ABACUS #1860, CODEX #977 and private QPS #1959. Selected 2026-10-18 job observations only; no automatic refresh, credential ingestion, QPS confidential asset import, authenticated dispatch, security waiver, merge approval or root closure.

The execution DAG is a typed origin → candidate → test → runner → receipt → consumer projection with native historical jobs entering only at the *origin*, never to prove a later candidate. Its common proof fan-in is guarded by the independent admission gate; declaration links are not proof. Cycles, duplicate jobs, unpinned heads, impossible failure dispositions and overlapping write paths fail closed. A typed universal reference graph may cycle; the executable DAG must not.

## Concurrent wave slices

| Lane | Owner | Source origin | Candidate / upstream | Next actual proof |
|---|---|---|---|---|
| A · W29 comparator | ABACUS | #2256, exact native W29 #39154971255 | #2261 | 4/4 matched test+coverage artifact pairs |
| B · G3CS B0 | ABACUS | #2247, B0 #39152559218 | #2262 | B0 test census with typed optional-zip skip |
| C · Unified SPINE | CODEX | #1104, native #39156209801 four jobs PASS | W30 own draft | 4-cell artifact hash/graph testflight |
| D · Receiver handoff | CODEX+remote owners | ABACUS #2255 peer 1/1 success, QPS #1957 | CODEX #977 stage-only | Two-sided independently verified artifact consumption |
| E · P0 authority | Repository administrators | ABACUS #1860 / QPS #1959 | No agent write | Effective protections, independent human review, blocked RED canary |

**No collision among concurrently changed paths:** A touches W29 workflow and test, B touches G3CS W10 test and one guard, C adds its own files, D/E are non-mutating. No shared-file write leases. Completed or merged PRs are historical facts, not admission credit.

## Independent metrics and N−1/N/N+1

- W29 prior **N−1**: four platform cells reached first red at *baseline coverage collection* ("No data to report"), 0/4 complete.
- W29 subsequent **N**: same four OS/Python cells progressed to baseline+expanded suite execution; four first reds moved to **comparator module import**. Exactly 4/4 cell stage displacements, still 0/4 complete. Different head SHAs, so no matched coverage-gain or root-closure claim.
- CODEX five-axis baseline: 4/4 native jobs PASSED, artifact publication steps succeeded. W30 graph pipeline needs new exact candidate receipts and independent governance.
- **N+1**: defined by per-lane acceptance. No forecast treated as a measured result.
- First-red manifestation density, unique root fingerprints, downstream reach, owner gate pressure, native-pair coverage, queue time and root closure are *separate*; unknown values remain `null`.

## Rebuild and verify

```bash
python mission_control/mycelium/five_axis/spine_w30.py --input mission_control/mycelium/five_axis/W30_SELECTED_NATIVE.json --out /tmp/w30-spine --head <exact 40-char head>
python mission_control/mycelium/five_axis/spine_w30.py --input mission_control/mycelium/five_axis/W30_SELECTED_NATIVE.json --out /tmp/w30-spine --head <exact 40-char head> --verify-only
python -m unittest discover -s tests -p 'test_five_axis_spine_w30.py' -v
```

Source-bound outputs: `W30_SPINE_GRAPH.json`, `W30_SPINE_METRICS.json`, `W30_SIPOC.json`, portable `W30_VIEWER.html` and `W30_SHA256.json`. Their hashes are checked against exact candidate source SHA; never interpret portable viewer output as a completed live federated handshake.

## Hold boundaries

Existing merges are recorded separately from governed merges. The public CODEX static control plane cannot mutate ABACUS or private QPS. Read-only preview may proceed despite P0; release promotion requires effective required statuses, owner approval, A10/security, red-canary denial, exact-head terminal checks, and subsequent main SHA readback. Preserve all historic lineages, including first-red displacement and failed/queued runs.
