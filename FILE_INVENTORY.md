# ABACUS File Inventory Audit

## Read this first: not ground truth from Codex

A direct `git clone https://github.com/GBOGEB/ABACUS.git` was attempted from this container, but the environment's GitHub CONNECT tunnel returned HTTP 403. Therefore this file is **not a measured clone inventory**. Treat it as a checklist/hypothesis for what to verify on the Windows machine, not as authoritative file counts or sizes.

The authoritative inventory must come from the local PowerShell audit in `ABACUS_LOCAL_GROUND_TRUTH_AUDIT.ps1`, which writes `_AUDIT\TRACKED_files.txt`, `_AUDIT\FOLDER_MAP.csv`, `_AUDIT\EMBEDDED_repos.txt`, and `_AUDIT\BACKUP_folders.txt` in the real Windows workspace.

## Repository-level counts to verify locally

| Metric | Current status | Ground-truth source |
|---|---|---|
| Tracked file count | Not measured by Codex; user context says ~3,271 | `_AUDIT\TRACKED_files.txt` line count |
| Total tracked byte size | Not measured by Codex | Run the size command below in a successful local clone |
| Top-level folder counts/sizes | Not measured by Codex | Local `git ls-files` grouped by top-level folder |
| File-type distribution | Not measured by Codex | Local `git ls-files` grouped by extension |

## Minimum local commands for exact counts

```powershell
$root = "C:\Users\gbonthuy\OneDrive - Studiecentrum voor Kernenergie\Master_Input"
Set-Location $root
git --no-pager ls-files > "_AUDIT\TRACKED_files.txt"
(Get-Content "_AUDIT\TRACKED_files.txt").Count
```

For exact tracked sizes, run from a Git Bash or another shell with `stat`, or adapt the same list to PowerShell `Get-Item`:

```powershell
Get-Content "_AUDIT\TRACKED_files.txt" | ForEach-Object {
    $p = Join-Path $root $_
    if (Test-Path $p) { [PSCustomObject]@{ Path = $_; Bytes = (Get-Item $p).Length } }
} | Export-Csv "_AUDIT\TRACKED_sizes.csv" -NoTypeInformation
```

## Structural folders to verify

The previous public-surface review saw these broad categories, but exact counts/sizes must be filled from the local audit:

| Category | Folders / patterns | Provisional action |
|---|---|---|
| Active core candidates | `src/`, `DMAIC_V3/`, `local_mcp/`, `scripts/`, `tools/`, `tests/`, `.github/`, `docs/`, `governance/`, `rtm/`, `ssot/`, `patterns/` | Keep if tracked and tested |
| GitHub-visible snapshot bloat | `ABACUS-v031/`, `ABACUS-v032/`, `ABACUS-UNIFIED/`, `ABACUS_V21_DEPLOYMENT_PACKAGE/` | Compare for uniqueness, then archive/split/remove from active repo |
| Generated or churn-heavy candidates | `DMAIC_V3_OUTPUT/`, `reports/`, `logs/`, `DOW_LOGS/`, `staging/`, `demo_workspace/` | Ignore or move to artifacts after preserving intentional outputs |
| Local-only candidates to protect first | `rich_padding/`, `CODESPACES_jyperter/`, `codex_project/`, `integration_DOW_KEB_MASTER/` | Verify with `_AUDIT\FOLDER_MAP.csv`; split/push/archive before cleanup |

## File-type distribution

Not measured here. The expected distribution is likely dominated by Markdown, Python, JSON/YAML, and generated HTML, but the exact `.py`, `.md`, `.json`, `.yml`, etc. counts should be generated from `_AUDIT\TRACKED_files.txt`.
