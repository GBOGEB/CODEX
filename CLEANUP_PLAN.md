# ABACUS Cleanup Plan

## First principle: ground truth before cleanup

The previous Codex clone attempt failed with HTTP 403, so these documents must be treated as a hypothesis/checklist until the Windows workspace audit is run. The cleanup sequence starts with `ABACUS_LOCAL_GROUND_TRUTH_AUDIT.ps1`; do not delete, ignore, or move local-only folders before reviewing `_AUDIT\FOLDER_MAP.csv`.

## Target principle: one project, one repo

ABACUS should converge to one primary source repository containing active source, tests, current docs, and curated configuration only. Historical snapshots, generated reports, local experiments, and independent projects should be archived or split.

## Proposed target structure

```text
ABACUS/
├── README.md
├── pyproject.toml / requirements files
├── src/                         # importable ABACUS package
├── DMAIC_V3/                    # active DMAIC engine, or migrate into src/abacus/dmaic
├── local_mcp/                   # active MCP/orchestration code, renamed modules where needed
├── scripts/                     # CLI/maintenance scripts only
├── tools/                       # reusable tools; migrate tools_v2.3 here or archive
├── tests/                       # all automated tests
├── docs/                        # current human docs source
├── docs/archive/                # curated historical docs only, not generated dumps
├── governance/                  # DOW/governance config/docs
├── rtm/                         # requirements traceability source
├── ssot/                        # canonical indexes and schemas
├── patterns/                    # curated reusable patterns/schemas
└── .github/workflows/           # consolidated CI/CD workflows
```

## Ordered recommendations

### Phase 0 — Run the local ground-truth audit

1. Open a fresh PowerShell window on the Windows machine.
2. Run `ABACUS_LOCAL_GROUND_TRUTH_AUDIT.ps1` or paste its contents.
3. Review `_AUDIT\FOLDER_MAP.csv`, `_AUDIT\EMBEDDED_repos.txt`, `_AUDIT\TRACKED_files.txt`, and `_AUDIT\BACKUP_folders.txt`.
4. Use `_AUDIT\FOLDER_MAP.csv` as the source of truth for `TRACKED` versus `GHOST (not in ABACUS)`.

### Phase 1 — Protect local-only work

1. If `rich_padding` is an embedded repo and ghost, move it out of ABACUS and push it to its own GitHub repo.
2. If `CODESPACES_jyperter` is an embedded repo and ghost, move it out of ABACUS and push it to its own GitHub repo.
3. If `codex_project` is ghost and tiny/scratch, archive it or intentionally absorb it into ABACUS; if it is real source, split/push first.
4. If `integration_DOW_KEB_MASTER` is ghost and real integration code, intentionally absorb it into ABACUS or split it; if scratch, archive it.

### Phase 2 — Keep active ABACUS core

Keep these as the ABACUS core unless the exact local audit disproves current use:

- `src/`
- `DMAIC_V3/`
- `local_mcp/`
- `scripts/`
- `tools/`
- `tests/`
- `.github/`
- `docs/` current docs source
- `governance/`, `rtm/`, `ssot/`, `patterns/`

### Phase 3 — Archive or split historical version streams

After comparing for unique content, archive/split these rather than keeping them in the active repo root:

- `ABACUS-v031/`
- `ABACUS-v032/`
- `ABACUS-UNIFIED/`
- `ABACUS_V21_DEPLOYMENT_PACKAGE/`
- `tools_v2.3/` after migrating active tools
- `tracking_v2.3/` except canonical live task data
- `workflows-to-install/` after workflow activation is resolved

Recommended destination: `GBOGEB/ABACUS-archive` or GitHub releases, not the active source tree.

### Phase 4 — Remove generated outputs from source control

Move or ignore generated/churn-heavy material only after checking whether any outputs are intentionally versioned:

- `DMAIC_V3_OUTPUT/`
- non-whitelisted `reports/`
- `logs/`
- rolling `DOW_LOGS/`
- generated dashboards where reproducible from source
- generated `.pptx`, archives, CSV/parquet/HDF5, DB files

### Phase 5 — Consolidate documentation

1. Keep `docs/` for current docs.
2. Keep `docs_versioned/` only for curated version history that users need.
3. Move one-off files matching `*_STATUS_*.md`, `*_REPORT_*.md`, `*_SUMMARY.md`, `SESSION_HANDOVER_*.md` to `docs/archive/YYYY-MM/` or an archive repo.
4. Consolidate `handover/`, `deepagent-handover-package/`, `myrrha_handover/`, and `section_readmes/` into a single `docs/handover/` source plus generated artifacts outside Git.

### Phase 6 — Python/module cleanup

1. Rename dotted Python filenames such as `agent_orchestrator_v3.0.py` to importable names like `agent_orchestrator_v3_0.py`, with temporary compatibility wrappers if needed.
2. Remove or mark stub-only/version-stamped agents once the active implementation is verified.
3. Consolidate root scripts into `scripts/` or `tools/` with CLI entry points.
4. Reduce multiple orchestrator variants to one canonical orchestrator plus documented adapters.

## Folder disposition summary

| Disposition | Folders |
|---|---|
| Keep core | `src/`, `DMAIC_V3/`, `local_mcp/`, `scripts/`, `tools/`, `tests/`, `.github/`, `docs/`, `governance/`, `rtm/`, `ssot/`, `patterns/` |
| Split/push if ghost | `rich_padding/`, `CODESPACES_jyperter/` |
| Archive or absorb after audit | `codex_project/`, `integration_DOW_KEB_MASTER/` |
| Archive/split historical snapshots | `ABACUS-v031/`, `ABACUS-v032/`, `ABACUS-UNIFIED/`, `ABACUS_V21_DEPLOYMENT_PACKAGE/`, `deepagent-handover-package/`, `myrrha_handover/`, `section_readmes/`, `workflows-to-install/` |
| Ignore/generated after review | `DMAIC_V3_OUTPUT/`, most of `reports/`, `logs/`, rolling `DOW_LOGS/`, `staging/`, scratch/demo workspaces |
