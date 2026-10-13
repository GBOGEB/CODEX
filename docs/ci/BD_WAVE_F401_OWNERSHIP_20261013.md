# CODEX BD Wave A — Frozen scope and disjoint ownership

Authority: CODEX #989. Source B1: run 38401729646, artifact 11815412295, PR merge-ref SHA `5d7701d01d23bf51574eb9d08cecfb2952ed87d5`. Census: Ruff 182; Pyright 0 in one file only. Do not extrapolate to full repository.

## Scout and Deep Reader
- Scout: partition exact B1 diagnostics by `path`, independently of rule, to prevent double editing.
- Deep Reader: classify import-order side effects, exception semantics, command-line entrypoint behavior and generated-output consumers before code changes.
- Historian: check merged #1011/#1012 lineage, original evidence hashes, and open work, preventing duplicate repair branches.

## Exclusive repair ownership, first wave
T1-F401 owns:
- scripts/build_missioncontrol_metrics.py
- scripts/check_bridge_alignment.py
- scripts/check_pages_deploy_concurrency.py
- scripts/check_svg_links.py
- scripts/id_work_conserving_scheduler.py
- scripts/validate_census_dov_tuple.py

T3-I001: excludes all six T1 paths; remaining import-order paths require a separate, per-file frozen assignment before mutation.
T4-EXE001/F541: excludes T1 and all subsequently allocated T3 paths.
T2-Pyright: read-only scope expansion first, then allocate modules that are not owned by T1/T3/T4.
R1: independent review of all changes, run receipts, failure cases, and no authority changes.

## Execution claims
Six files changed on an isolated branch, targeting seven F401 diagnostics. These are code changes by a repository-authorized operator, **not** an authenticated GM crew spawn. No accepted burndown or CI PASS is claimed before exact-head jobs and B2 JSON receipts.

No QPS engineering authority transfer; no automatic acceptance, merge, or controlled-crew eligibility bypass.
