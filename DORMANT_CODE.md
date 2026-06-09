# ABACUS Dormant Code Audit

> Scope note: exact dormant Python analysis requires a clone and source-content scan. Because `git clone` was blocked in this container, this report separates high-confidence structural dormant signals from items that need a local rerun.

## Python files never imported elsewhere

A definitive import graph was not computed. However, the repository's own dashboard and README identify several candidates that should be treated as dormant, duplicated, or compatibility-only until tested:

| Candidate / pattern | Reason |
|---|---|
| `*_corrupted.py` | Dashboard reports `full_pipeline_orchestrator_corrupted.py` contains merge conflict markers and that content is available in a fixed variant. |
| Root-level one-off deployment/roundtrip scripts | README lists multiple root scripts (`deploy_full_integration.py`, `run_comprehensive_deployment.py`, `run_streamlined_deployment.py`, `run_cicd_roundtrip_test.py`) that should be consolidated into `scripts/` or `tools/`. |
| `DMAIC_V3/local_mcp/agents/*_v2.3_OPTIMIZED.py` stubs | `code_index.yaml` identifies many v2.3 agent files as `0.0.0-stub`; keep only if they are compatibility placeholders. |
| Multiple orchestrator variants | Dashboard says 4 pipeline orchestrator variants need consolidation study. |
| `local_mcp/agent_orchestrator_v3.0.py` | README says it is an active compatibility wrapper, but dotted filenames are not directly importable as Python module names; keep but consider renaming with a compatibility shim. |

## One-off Markdown/report files

The root listing contains many status/report/handover files that look like one-time execution artifacts rather than durable source documentation. Patterns to archive under `docs/archive/YYYY-MM/` or move out of the source repo:

- `*_STATUS_*.md`
- `*_REPORT_*.md`
- `*_SUMMARY.md`
- `*_COMPLETE_SUMMARY.md`
- `SESSION_HANDOVER_*.md`
- `CICD_ITERATION_*_REPORT.md`
- `ABACUS_V21_*SUMMARY.md`
- `*_DEPLOYMENT_COMPLETE_SUMMARY.md`
- `*_MIGRATION_COMPLETION_SUMMARY.md`

Visible examples include `ABACUS_V21_COMPLETE_SESSION_SUMMARY.md`, `ABACUS_V21_DEPLOYMENT_COMPLETE_SUMMARY.md`, `CICD_HANDOVER_REPORT.md`, `CICD_ITERATION_1_COMPLETION_REPORT.md`, `CICD_ITERATION_2_COMPLETION_REPORT.md`, and `CICD_ROUNDTRIP_TEST_REPORT.md`.

## Duplicate or near-duplicate clusters

| Cluster | Why it is likely duplicate / near-duplicate |
|---|---|
| `ABACUS-v031/`, `ABACUS-v032/`, `ABACUS-UNIFIED/`, `ABACUS_V21_DEPLOYMENT_PACKAGE/` | Version snapshots appear to preserve historical streams inside the active repo. |
| `docs/`, `docs_versioned/`, `handover/`, `deepagent-handover-package/`, `myrrha_handover/`, `section_readmes/` | Multiple documentation/handover roots likely overlap. |
| `tools/`, `tools_v2.3/`, `scripts/`, root Python scripts | Tooling is split across several eras/locations. |
| `qplant/` and `content/qplant/` | Domain content appears duplicated across source/content roots. |
| `reports/`, `DMAIC_V3_OUTPUT/reports/`, `logs/`, `DOW_LOGS/`, `metrics/federation/` | Generated output and metrics are partially versioned and partially ignored. |

## Exact local rerun commands

```bash
python -m compileall .
python repo_analysis_toolkit/analyze_repo.py --repo . --out reports/baseline.json
python repo_analysis_toolkit/classify_artifacts.py --repo . --out reports/classification.csv --dedup
```
