# ABACUS Embedded Repository Audit

## Read this first: Codex could not run the authoritative gitlink scan

A direct clone was blocked by HTTP 403 in this container, so nested `.git` directories and `160000` gitlink entries were **not** measured from a local ABACUS clone. This report is a local-audit runbook plus the one useful public-surface signal: the named folders were not visible in the GitHub ABACUS surface checked from this session.

## Required local audit files

Run `ABACUS_LOCAL_GROUND_TRUTH_AUDIT.ps1` on the Windows machine. It writes:

| File | Meaning |
|---|---|
| `_AUDIT\EMBEDDED_repos.txt` | Every nested folder below root that owns its own `.git` directory |
| `_AUDIT\FOLDER_MAP.csv` | Top-level folders classified as `TRACKED` or `GHOST (not in ABACUS)` |
| `_AUDIT\TRACKED_files.txt` | The root ABACUS repo's tracked file list |

## Required checks

| Target | Public GitHub surface status from Codex | Decision rule after local audit |
|---|---|---|
| `rich_padding` | Not visible in GitHub ABACUS from the checks available here | If `_AUDIT\FOLDER_MAP.csv` says `EMBEDDED-REPO` + `GHOST`, split to its own GitHub repo before cleanup |
| `CODESPACES_jyperter` | Not visible in GitHub ABACUS from the checks available here | If `_AUDIT\FOLDER_MAP.csv` says `EMBEDDED-REPO` + `GHOST`, split to its own GitHub repo before cleanup |
| `codex_project` | Not visible in GitHub ABACUS from the checks available here | If ghost and tiny/scratch, archive or absorb intentionally; if real source, push/split first |
| `integration_DOW_KEB_MASTER` | Not visible in GitHub ABACUS from the checks available here | If real integration code, absorb into ABACUS intentionally or split; if scratch, archive |

## Gitlinks and submodules

The local audit script finds nested `.git` directories. If you also need true submodule/gitlink entries, run this in the root ABACUS repo on the Windows machine:

```powershell
git --no-pager ls-files --stage | Where-Object { $_ -match '^160000 ' }
```

Any `160000` row is a gitlink: GitHub stores only the referenced commit pointer, not the nested repo's file contents.

## Practical conclusion

Do **not** delete or ignore local-only folders until `_AUDIT\FOLDER_MAP.csv` is reviewed. If `rich_padding` or `CODESPACES_jyperter` are embedded repos with substantial code, the clean action is to move them out of ABACUS and push them as independent repositories.
