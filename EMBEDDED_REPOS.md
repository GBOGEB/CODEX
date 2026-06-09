# ABACUS Embedded Repository Audit

> Scope note: direct clone was blocked by HTTP 403 in this container, so nested `.git` directories and gitlink entries could not be verified with `find`/`git ls-files --stage`. Findings below are based on the visible GitHub root, repository raw files, and targeted web searches.

## Required checks

| Target | Visible at ABACUS root? | Evidence / interpretation | Content present in GitHub ABACUS? |
|---|---:|---|---|
| `rich_padding` | No | Not listed in the GitHub root directory listing; targeted web search did not find it in `GBOGEB/ABACUS`. | No visible content in GitHub ABACUS. If it exists locally, it is local-only or untracked elsewhere. |
| `CODESPACES_jyperter` | No | Not listed in the GitHub root directory listing; targeted web search did not find it in `GBOGEB/ABACUS`. | No visible content in GitHub ABACUS. If it exists locally, it is local-only or untracked elsewhere. |
| `codex_project` | No | Not listed in the GitHub root directory listing; targeted web search did not find it in `GBOGEB/ABACUS`. | No visible content in GitHub ABACUS. If it exists locally, it is local-only or untracked elsewhere. |
| `integration_DOW_KEB_MASTER` | No | Not listed in the GitHub root directory listing; targeted web search did not find it in `GBOGEB/ABACUS`. | No visible content in GitHub ABACUS. If it exists locally, it is local-only or untracked elsewhere. |

## Gitlinks and submodules

- `.gitmodules` was not available through raw GitHub access in this session; the browser returned only the accessible `.gitignore` result when both were requested.
- The GitHub root page did not show obvious submodule labels for the required target names.
- A definitive gitlink audit still requires this command inside a successful clone:

```bash
git ls-files --stage | awk '$1 == "160000" {print}'
find . -mindepth 2 -type d -name .git -print
```

## Practical conclusion

The four explicitly named folders do **not** appear to have their contents present in GitHub ABACUS. If those directories exist in the user's Windows `Master_Input` workspace, treat them as **not captured by this GitHub repo** until proven otherwise by a local `git status`/`git ls-files` run.
