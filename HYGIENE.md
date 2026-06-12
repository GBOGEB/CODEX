# ABACUS Repository Hygiene Audit

## Read this first: measurements must come from the Windows workspace

Exact backup sizes, path lengths, and recoverable history size were not measured by Codex because the GitHub clone was blocked. This file is a conservative hygiene checklist to apply after the local `_AUDIT` outputs exist.

## Backup / generated folders to measure first

| Folder / pattern | Risk | Recommendation |
|---|---|---|
| `BACKUPS/`, `Backups/`, `backup/`, `*_backup.*`, `*.bak`, `*.backup` | Snapshot bloat and stale files | Record in `_AUDIT\BACKUP_folders.txt`, archive what matters, then ignore/delete old snapshots |
| `ABACUS-v031/`, `ABACUS-v032/`, `ABACUS-UNIFIED/`, `ABACUS_V21_DEPLOYMENT_PACKAGE/` | Version snapshots inside active repo | Compare for uniqueness, then archive/split/remove from active repo |
| `DMAIC_V3_OUTPUT/`, `reports/`, `logs/`, `DOW_LOGS/` | Generated output and runtime churn | Track only intentional status JSON or `.gitkeep`; move the rest to artifacts |
| `deepagent-handover-package/`, `myrrha_handover/`, `handover/`, `section_readmes/` | Repeated generated docs/handover dumps | Consolidate current docs, archive historical handovers |
| `staging/`, `demo_workspace/`, `workflows-to-install/` | Scratch/staging material | Archive or ignore after extracting source/config that is still needed |

## Windows path-length risk

Run this after `_AUDIT\TRACKED_files.txt` exists:

```powershell
Get-Content "_AUDIT\TRACKED_files.txt" |
  Where-Object { $_.Length -gt 200 } |
  Sort-Object Length -Descending |
  ForEach-Object { "{0}`t{1}" -f $_.Length, $_ } |
  Out-File "_AUDIT\LONG_PATHS_over_200.txt"
```

Any result is a Windows/OneDrive portability risk and should be flattened, renamed, or archived.

## Recommended `.gitignore` additions

Add these only after local-only real code has been split/pushed or archived:

```gitignore
# Uppercase and refactoring backup folders
BACKUPS/
Backups/
refactoring_*/
*_refactoring_backup*/

# Generated audit/report outputs, unless intentionally whitelisted
_AUDIT/
*_STATUS_*.md
*_REPORT_*.md
SESSION_HANDOVER_*.md
DMAIC_V3_OUTPUT/

# Local nested repo workspaces: ignore only after splitting/pushing/archiving
rich_padding/
CODESPACES_jyperter/
codex_project/
integration_DOW_KEB_MASTER/
```

## Recoverable-space estimate

The exact recoverable space is not known yet. Prioritize measurement in this order:

1. `BACKUPS/` and recursively found backup folders from `_AUDIT\BACKUP_folders.txt`.
2. Version snapshots: `ABACUS-v031/`, `ABACUS-v032/`, `ABACUS-UNIFIED/`, `ABACUS_V21_DEPLOYMENT_PACKAGE/`.
3. Generated outputs: `DMAIC_V3_OUTPUT/`, `reports/`, `logs/`, `DOW_LOGS/`.
4. Handover packages and generated dashboards.
