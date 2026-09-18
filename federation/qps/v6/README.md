# QPS v6 CODEX Local Preflight / Publication Entry

Parent: `GBOGEB/cryoplant-project#1379`  
Publication issue: `GBOGEB/CODEX#753`  
QPS role boundary: CODEX validates/governs/publishes sanitized projections; it does not own QPS engineering or bidder disposition.

## Exact pins after administrative merge refresh

- CODEX: `23624e10478e115bcea2613bfcd41c24eb5dea24`
- QPS: `bb6f09e90a6af86e2601d3bad706209fa429eadc`
- ABACUS: `b4094dbabf1bc2d750fdc0803d4ccc25ca5cf524`

## Existing local preconfiguration

- Python: `>=3.11` from root `pyproject.toml`.
- Dev: pytest + pytest-json-report + pinned `ruff==0.16.6`.
- TypeScript test runtime: `tsx` via `package.json`.
- Container: root `Dockerfile` combines Python 3.11 and Node 22 and runs `scripts/validate_all.py`.
- Compose: `compose.yaml` exposes the canonical validator service.
- Devcontainer: Python 3.11 with editable install.
- LLDB/DAP/Swift/Docker/runner/MCP census/probe: `scripts/lldb_dap_runtime_probe.py`.

Observed repo-level editor gaps:

- no root `.vscode/launch.json`, `.vscode/tasks.json`, or `.vscode/settings.json`;
- no root `cspell.json`;
- no root `.pre-commit-config.yaml`.

These are tracked as usability/admin gaps, not QPS engineering defects.

## Local preflight contract

1. install exact dependencies from the repository;
2. run `python -m pytest`;
3. run `ruff` on the release-relevant Python surface;
4. run `npm test`;
5. run `python scripts/validate_all.py`;
6. build/run the canonical validator container;
7. run LLDB/DAP census; real Swift/LLDB proof may DEFER off macOS;
8. emit exact-SHA receipt with test counts, tool versions and hashes.

## Publication DoD

- only `.github/workflows/pages.yml` is authoritative for QPS v6;
- non-authoritative deployers cannot overwrite the same Pages root;
- published site carries release ID and exact QPS/CODEX/ABACUS pins;
- publication input is sanitized/publishable;
- link/stale/manifest checks pass;
- run ID, deployment ID and Pages artifact digest are returned to QPS.

No Pages PASS can compensate QPS runtime GOLD `#923`.
