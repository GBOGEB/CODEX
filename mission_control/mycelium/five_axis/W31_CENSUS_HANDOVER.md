# CODE PURPLE W31 — exact-main census and stop-condition handover

Read-only continuation of CODEX MYCELIUM W30, not another source of truth or remote scheduler. W30 historical topology and 14 pinned job observations remain unchanged.

## Pinned source and lineage
- CODEX main observed: `774d51eb4a58fa259f059764e586d12a7935b2e1`
- ABACUS main observed: `994ad6e73c748923841d92b12651e92d41b2d4ff`
- W30 native four-cell PASS: [39158510448](https://github.com/GBOGEB/CODEX/actions/runs/39158510448), four published artifacts. This is native graph qualification, **not** verified ABACUS W29 source coverage or QPS receiver acceptance.
- W31 GitHub readback is **frozen**, current for collection time only, not an ongoing poll or entire-fleet census. First-page tails stay UNKNOWN.

## Guarded execution
1. Deduplicate run identities, preserve attempts and statuses; a retry does not create another unique run. Detect replay conflicts.
2. Separate queue saturation (nonterminal status) from accepted functional proof; at observed nonterminal fraction >=80%, propose just one new independent lane, no repeated full-suite reruns.
3. Keep five axis numerators/denominators unknown without same source SHA, identical eligible scope/config SHA256, native terminal acceptance and stable denominator. Three successive flat matched deltas (four epochs) are required for local stability. Below target, pivot rather than claim completion.
4. Group first-red manifestations by explicit fingerprint only; accepted causal closures remain unknown. Historical merge states never confer governed admission.
5. Exact candidate-head native workflow runs the regression suite and emits hash-verified `W31_CENSUS_REPORT.json` and `W31_SHA256.json`. No tokens, owner permission changes, secret payload, cross-repository mutation, or worker dispatch.

## Reproduction

```bash
python -m unittest discover -s tests -p 'test_five_axis_census_w31.py' -v
python mission_control/mycelium/five_axis/census_w31.py --input mission_control/mycelium/five_axis/W31_FRESH_READBACK.json --out /tmp/w31 --head <exact-40-char-head>
python mission_control/mycelium/five_axis/census_w31.py --input mission_control/mycelium/five_axis/W31_FRESH_READBACK.json --out /tmp/w31 --head <exact-40-char-head> --verify-only
```

## NEXT checkpoint
Fetch new immutable API readbacks (main refs, runs, attempts, jobs, artifacts, exact SHA); append a new epoch without overwriting W31. Reconcile ABACUS W29 current source-owned repair and B0/NetworkX first-reds against terminal native jobs. CODEX receiver and QPS owner must supply independent readbacks. Admin must install effective required checks and independent review with blocked RED canary before any governed admission.

`MERGE_ADMISSION=HOLD`; `mutation_enabled=false`; `authority_transfer=false`; `formal_root_closures=UNKNOWN`.
