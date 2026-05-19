# Copilot Instructions for CODEX

- Keep changes scoped and avoid unrelated refactors.
- Preserve the platform boundary: CODEX owns GitHub integration substrate concerns.
- For code changes, run the same checks as CI from the repo root:
  - `python -m pytest -q`
  - `python scripts/check_manifest.py`
  - `python scripts/check_globs.py`
  - `python scripts/check_stale.py`
  - `python scripts/check_links.py`
- If adding new HTML entrypoints under `docs/`, update `MANIFEST.json` so stale checks continue to pass.
