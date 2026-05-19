# Copilot instructions for CODEX

- Keep changes surgical and scoped to the requested issue or comment.
- Prefer documentation-first governance updates unless runtime changes are explicitly requested.
- For code changes, run the CI-equivalent checks from repository root:
  - `python -m pytest -q`
  - `python scripts/check_manifest.py`
  - `python scripts/check_globs.py`
  - `python scripts/check_stale.py`
  - `python scripts/check_links.py`
- Avoid unrelated refactors in mixed governance/runtime pull requests.
