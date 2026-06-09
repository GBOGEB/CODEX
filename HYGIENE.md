# ABACUS Repository Hygiene Audit

> Scope note: exact sizes and path lengths require a clone. This report records the high-confidence hygiene issues visible from GitHub and the `.gitignore` policy that was accessible through raw GitHub.

## Backup / generated folders

| Folder / pattern | Visible or ignored? | Risk | Recommendation |
|---|---|---|---|
| `ABACUS-v031/`, `ABACUS-v032/`, `ABACUS-UNIFIED/`, `ABACUS_V21_DEPLOYMENT_PACKAGE/` | Visible top-level folders | Version snapshots inflate repo and blur active source | Archive/split after preserving unique source |
| `DMAIC_V3_OUTPUT/reports/` | Visible nested reports path | Generated reports in source tree | Ignore or move to CI artifacts |
| `reports/` | Top-level folder with `.gitignore` exceptions | Mixed generated and blessed JSON | Keep only curated status JSON; ignore all other generated reports |
| `logs/` and `DOW_LOGS/` | Visible top-level folders | Runtime churn and large history | Track `.gitkeep` plus blessed dashboard JSON only |
| `deepagent-handover-package/`, `myrrha_handover/`, `handover/`, `section_readmes/` | Visible doc/handover clusters | Repeated generated docs | Consolidate current docs; archive historical handovers |
| `staging/`, `demo_workspace/`, `workflows-to-install/` | Visible top-level folders | Scratch/staging material in main repo | Archive or ignore after extracting source |
| `backup/`, `*_backup.*`, `*.bak`, `*.backup` | Already ignored by `.gitignore` | Good baseline | Extend to uppercase `BACKUPS/` and `refactoring_*` |

## Windows path-length risk

The visible path `qcell_svg_model/v0_8_1_option_b/handover/v1_1_full/` is already deep enough that child files can exceed 200 characters. This is a Windows portability risk, especially under OneDrive paths with spaces and long organization names.

Exact local check:

```bash
git ls-files | awk 'length($0) > 200 {print length($0), $0}' | sort -nr
```

## Recommended `.gitignore` additions

The existing `.gitignore` already covers Python caches, virtual environments, logs, env files, generated reports, temp files, archives, CSV/parquet/HDF5, DB files, backup files, and generated PowerPoint files. Add or verify these more explicit cleanup-focused rules:

```gitignore
# Uppercase and refactoring backup folders
BACKUPS/
Backups/
refactoring_*/
*_refactoring_backup*/

# Generated audit/report outputs, unless intentionally whitelisted
*_STATUS_*.md
*_REPORT_*.md
SESSION_HANDOVER_*.md
DMAIC_V3_OUTPUT/

# Local nested repo workspaces that should not be silently swallowed
rich_padding/
CODESPACES_jyperter/
codex_project/
integration_DOW_KEB_MASTER/
```

If any of the local nested repo workspaces are real source projects, do **not** just ignore them permanently; first split/push them to their own GitHub repositories.

## Estimated recoverable space

The precise recoverable space could not be measured without a clone. Structurally, the highest-probability space recovery is in:

1. Version snapshots: `ABACUS-v031/`, `ABACUS-v032/`, `ABACUS-UNIFIED/`, `ABACUS_V21_DEPLOYMENT_PACKAGE/`.
2. Generated reports/logs: `DMAIC_V3_OUTPUT/reports/`, `reports/`, `logs/`, `DOW_LOGS/`.
3. Handover packages: `deepagent-handover-package/`, `myrrha_handover/`, `section_readmes/`.
4. Generated dashboards and office/archive artifacts.

To estimate history cleanup after removing backups from the index, run:

```bash
git count-objects -vH
git filter-repo --analyze
```
