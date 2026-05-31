# Deployment Readiness and TODO Tracker

Generated: `2026-05-31T19:23:47.960895+00:00`
Status: **deployment-ready**
Completion: **100.0%**

## Deployment Checks

| ID | OK | Bytes | Path |
|---|---|---:|---|
| bridge_cli | True | 5068 | `docs/wave_packages/runtime/federation_bridge_cli.py` |
| ci_workflow | True | 1638 | `.github/workflows/runtime_federation_ci.yml` |
| plotly_dashboard | True | 1988 | `docs/wave_packages/runtime/pages/plotly_runtime_dashboard.html` |
| pages_bundle | True | 603 | `docs/wave_packages/runtime/pages/runtime_bundle_index.html` |
| runtime_status_md | True | 403 | `docs/wave_packages/runtime/out/runtime_status.md` |
| statistics_pca | True | 2164 | `docs/wave_packages/runtime/out/statistics_pca_report.json` |
| topology_graph | True | 439 | `docs/wave_packages/runtime/out/topology_runtime.mmd` |
| tests | True | 3018 | `tests/test_runtime_validation.py` |
| manifest | True | 2306 | `MANIFEST.json` |
| topology_runtime | True | 1584 | `docs/wave_packages/topology/topology_runtime.json` |

## Remaining TODOs

| Priority | Status | Item |
|---|---|---|
| high | external-config-required | Confirm GitHub Pages repository settings publish docs/ or workflow artifact |
| high | integration-required | Add real ABACUS feed source instead of default fixture payload |
| high | buildout-required | Build out runtime HTML/index generators so CSS templates render without KeyError and bundle index artifacts are emitted |
| high | framework-incomplete | Implement non-dry-run pages regeneration adapter in runtime_bridge (current execute mode records plan only) |
| high | next-build | Persist runtime history across CI runs |
| medium | partial | Add live Plotly hydration from generated JSON reports |
| medium | next-build | Add automated link checking for generated Pages bundle |
| medium | external-config-required | Add branch protection/status check policy after CI is stable |
| medium | next-build | Add release/promotion gate from PR branch to main |
