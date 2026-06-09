# ABACUS Cleanup Plan

> Scope note: this is a structural cleanup plan from public GitHub-visible information. Before deleting anything, perform a successful local clone audit and compare against the user's local-only nested repositories.

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

### Phase 0 — Protect local-only work

1. On the Windows machine, run the local nested-repo/ghost-file map for `rich_padding`, `CODESPACES_jyperter`, `codex_project`, and `integration_DOW_KEB_MASTER`.
2. If those folders exist locally and contain real code, push them to their own GitHub repositories before any cleanup.
3. If they are just scratch/generated workspaces, add them to `.gitignore` after archiving anything valuable.

### Phase 1 — Baseline exact metrics

1. Re-run the audit in an unrestricted clone with `git ls-files`, path-length checks, and `repo_analysis_toolkit`.
2. Produce exact file counts, sizes, extension distribution, import graph, and duplicate hashes.
3. Freeze a cleanup branch and avoid mixing feature work into cleanup commits.

### Phase 2 — Keep active core

Keep these as the ABACUS core unless the exact audit disproves current use:

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

Archive/split these after uniqueness comparison:

- `ABACUS-v031/`
- `ABACUS-v032/`
- `ABACUS-UNIFIED/`
- `ABACUS_V21_DEPLOYMENT_PACKAGE/`
- `tools_v2.3/` after migrating active tools
- `tracking_v2.3/` except canonical live task data
- `workflows-to-install/` after workflow activation is resolved

Recommended destination: `GBOGEB/ABACUS-archive` or GitHub releases, not the active source tree.

### Phase 4 — Remove generated outputs from source control

Move or ignore generated/churn-heavy material:

- `DMAIC_V3_OUTPUT/reports/`
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
2. Remove or mark stub-only v2.3 agents once the active implementation is verified.
3. Consolidate root scripts into `scripts/` or `tools/` with CLI entry points.
4. Reduce multiple orchestrator variants to one canonical orchestrator plus documented adapters.

## Folder disposition summary

| Disposition | Folders |
|---|---|
| Keep core | `src/`, `DMAIC_V3/`, `local_mcp/`, `scripts/`, `tools/`, `tests/`, `.github/`, `docs/`, `governance/`, `rtm/`, `ssot/`, `patterns/` |
| Archive/split | `ABACUS-v031/`, `ABACUS-v032/`, `ABACUS-UNIFIED/`, `ABACUS_V21_DEPLOYMENT_PACKAGE/`, `deepagent-handover-package/`, `myrrha_handover/`, `section_readmes/`, `workflows-to-install/` |
| Ignore/generated | `DMAIC_V3_OUTPUT/`, most of `reports/`, `logs/`, rolling `DOW_LOGS/`, `staging/`, scratch/demo workspaces |
| Verify local-only first | `rich_padding/`, `CODESPACES_jyperter/`, `codex_project/`, `integration_DOW_KEB_MASTER/` |
