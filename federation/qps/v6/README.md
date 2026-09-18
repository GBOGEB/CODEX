# QPS v6 CODEX Local Preflight / Publication Entry

Parent: `GBOGEB/cryoplant-project#1379`  
Publication issue: `GBOGEB/CODEX#753`  
QPS role boundary: CODEX validates/governs/publishes sanitized projections; it does not own QPS engineering or bidder disposition.

## Exact pins at creation

- CODEX: `76cfaf7be9776140ff8064f63b406d35b4fd3099`
- QPS: `48454561de70a8873f8fe2f32e4c9cbf8e31e51b`
- ABACUS: `33de3878ab0e5af0f5061c03844187bfc54a89d9`

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
