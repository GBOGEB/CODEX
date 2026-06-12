# ABACUS Dormant Code Audit

## Read this first: import analysis was not measured here

The previous Codex run could not clone ABACUS, so it could not compute a real Python import graph or duplicate-file hashes. This file is a shortlist of patterns to verify locally after `_AUDIT\TRACKED_files.txt` exists.

## Python dormant-code candidates to verify

| Candidate / pattern | Why to check |
|---|---|
| `*_corrupted.py` | Corrupted/merge-conflict variants should not remain active source if a fixed version exists |
| Root-level one-off deployment/roundtrip scripts | Scripts such as deployment or roundtrip test runners should live under `scripts/` or `tools/`, not as scattered root one-offs |
| `*_v2.3_OPTIMIZED.py` and other version-stamped variants | Version-stamped copies often indicate superseded code or compatibility shims |
| Multiple orchestrator variants | Keep one canonical orchestrator plus documented adapters/shims |
| Dotted Python filenames such as `agent_orchestrator_v3.0.py` | Dotted filenames are awkward to import as normal Python modules; prefer `_v3_0` naming with a compatibility wrapper if needed |

## One-off Markdown/report files

Archive or move generated report dumps after preserving anything still needed:

- `*_STATUS_*.md`
- `*_REPORT_*.md`
- `*_SUMMARY.md`
- `*_COMPLETE_SUMMARY.md`
- `SESSION_HANDOVER_*.md`
- `CICD_ITERATION_*_REPORT.md`
- `*_DEPLOYMENT_COMPLETE_SUMMARY.md`
- `*_MIGRATION_COMPLETION_SUMMARY.md`

## Duplicate or near-duplicate clusters to verify

| Cluster | Why it is likely duplicate / near-duplicate |
|---|---|
| `ABACUS-v031/`, `ABACUS-v032/`, `ABACUS-UNIFIED/`, `ABACUS_V21_DEPLOYMENT_PACKAGE/` | Version snapshots appear to preserve historical streams inside the active repo |
| `docs/`, `docs_versioned/`, `handover/`, `deepagent-handover-package/`, `myrrha_handover/`, `section_readmes/` | Multiple documentation/handover roots likely overlap |
| `tools/`, `tools_v2.3/`, `scripts/`, root Python scripts | Tooling is split across several eras/locations |
| `qplant/` and `content/qplant/` | Domain content may be duplicated across source/content roots |
| `reports/`, `DMAIC_V3_OUTPUT/`, `logs/`, `DOW_LOGS/`, `metrics/federation/` | Generated output and metrics are partially versioned and partially ignored |

## Local rerun suggestions

After the ground-truth audit, run import/duplicate analysis locally with the tools available in the repo or with PowerShell hashes:

```powershell
Get-Content "_AUDIT\TRACKED_files.txt" |
  Where-Object { $_ -like "*.py" } |
  Out-File "_AUDIT\PYTHON_tracked_files.txt"

Get-Content "_AUDIT\TRACKED_files.txt" |
  ForEach-Object {
    $p = Join-Path $PWD $_
    if (Test-Path $p) { Get-FileHash $p -Algorithm SHA256 | Select-Object Hash,@{Name='Path';Expression={$_}} }
  } | Export-Csv "_AUDIT\TRACKED_hashes.csv" -NoTypeInformation
```
