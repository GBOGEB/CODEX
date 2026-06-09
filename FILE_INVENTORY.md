# ABACUS File Inventory Audit

> Scope note: a direct `git clone https://github.com/GBOGEB/ABACUS.git` was attempted from this container, but the environment's GitHub CONNECT tunnel returned HTTP 403. This inventory is therefore based on the public GitHub repository page, raw files that were accessible through the browser channel, and repository self-reported documentation; it should be re-run with `git ls-files` in an unrestricted clone before destructive cleanup.

## Repository-level counts

| Metric | Observed / reported value | Source / confidence |
|---|---:|---|
| Git commits shown on GitHub root page | 1,786 | High: GitHub repository page |
| Tracked file count | ~3,271 | Medium: user-provided context; clone unavailable to verify |
| Repository dashboard commits snapshot | 558 | Medium: older/generated `docs/deep_analysis_dashboard.html` snapshot |
| GitHub Actions workflows | 37 active in README; dashboard also mentions 32 active + 2 legacy / 32 active + 5 staged | Medium: internally inconsistent historical docs |
| Total tracked byte size | Not verified | Requires `git ls-files -z | xargs -0 stat` in clone |

## Top-level folder inventory visible from GitHub root

The GitHub root listing exposes the following top-level directories. Exact per-folder file counts and sizes require an unrestricted clone; the cleanup priority is inferred from naming, README structure, and dashboard lineage.

| Top-level path | Visible status / purpose | Cleanup interpretation |
|---|---|---|
| `.devcontainer/` | Codespaces/dev-container configuration | Keep |
| `.github/` | Workflows and repo metadata | Keep, but consolidate workflows |
| `.vscode/` | Editor settings | Consider moving user-specific settings to ignore |
| `ABACUS-UNIFIED/` | Historical unified version stream | Archive or split after diffing against active engine |
| `ABACUS-v031/` | Historical/canonical foundation stream | Archive but preserve until canonical indexes are migrated |
| `ABACUS-v032/` | Historical production-pipeline stream | Archive/split; keep unique pipeline assets only |
| `ABACUS_V21_DEPLOYMENT_PACKAGE/` | Deployment package | Archive or release artifact, not active source |
| `DELTA_1/` | Delta artifact folder | Review then archive |
| `DMAIC_V3/` | Primary active DMAIC engine | Keep as core source |
| `DMAIC_V3_OUTPUT/reports/` | Generated output/report area | Should be ignored or moved to artifact storage |
| `DOW_LOGS/` | Dashboard/runtime JSON logs | Keep only intentionally versioned JSON; ignore rolling logs |
| `MINERVA_PID/` | Domain/project artifact area | Review; probably split/archive if not core runtime |
| `abacus_render_pipeline/A6_renderer_governance/TUPLE_OFFLOAD/` | Render pipeline/governance offload | Split into own module if active, otherwise archive |
| `analyses/compressors/` | Analysis artifacts | Archive generated analyses unless source-like |
| `analytics/runtime_convergence/` | Runtime analytics | Keep curated metrics, ignore generated outputs |
| `bridges/hbhs_ep_bridge/` | Bridge implementation/docs | Keep if referenced by workflows/tests |
| `content/qplant/` | QPLANT domain content | Keep curated source/domain docs |
| `core/` | Core code | Keep |
| `cryo_dashboard_v0_3_0/` | Dashboard version snapshot | Archive/split unless actively deployed |
| `deepagent-handover-package/` | Handover artifacts | Archive generated package; keep generator/source references |
| `demo_workspace/` | Demo workspace | Archive or move to examples if maintained |
| `dmaic-sprint-system/` | Sprint system | Review for active integration, otherwise split/archive |
| `docs/` | Current docs and dashboards | Keep, but separate generated HTML from source docs |
| `docs_versioned/` | Versioned/historical docs | Keep as archive, but move bulky history to docs archive repo if large |
| `federation/` | Federation logic/artifacts | Keep if active; otherwise archive generated outputs |
| `governance/` | Governance docs/config | Keep |
| `handover/` | Handover docs | Consolidate with `docs_versioned/handover/` |
| `integration/` | Integration code/docs | Keep if workflow-covered |
| `knowledge_packages/` | Knowledge packs | Keep curated packages; avoid generated copies |
| `local_mcp/` | Active local MCP/orchestrator/agents | Keep as core source |
| `logs/` | Logs | Ignore generated logs; keep `.gitkeep` only |
| `metrics/federation/` | Selected metrics JSON allowed by `.gitignore` | Keep only blessed dashboard JSON |
| `myrrha_handover/` | Handover/domain package | Archive/split unless actively referenced |
| `ontology/glossary/` | Glossary/ontology | Keep curated source |
| `patterns/scientific_visualization/` | Pattern/schema area | Keep schema/source patterns |
| `production/monitoring/` | Production monitoring | Keep active monitoring source/config |
| `qcell_svg_model/v0_8_1_option_b/handover/v1_1_full/` | Deep versioned handover/model path | Windows path-length risk; archive or flatten |
| `qplant/` | QPLANT source/domain area | Keep or consolidate with `content/qplant/` |
| `qplant_presentation_engine/` | Presentation engine | Split if substantial; otherwise keep under `tools/`/`src/` |
| `renderers/` | Renderer source | Keep if active |
| `repo_analysis_toolkit/` | Reusable cleanup toolkit | Keep; use it for the next full clone audit |
| `reports/` | Generated reports with some whitelisted JSON | Mostly ignore/archive; keep only intentional status JSON |
| `roadmaps/` | Planning docs | Archive stale roadmaps; keep current roadmap in docs |
| `rtm/` | Requirements trace matrix | Keep curated trace matrix |
| `rtm_integration/` | RTM integration | Keep if active |
| `runtime/` | Runtime source/artifacts | Keep active source; ignore ephemeral state |
| `scripts/` | Tool scripts | Keep and consolidate duplicate root scripts into here |
| `section_readmes/` | Generated/section README docs | Archive if redundant with docs site |
| `self_optimization/` | Self-optimization logic/docs | Keep if active, otherwise archive |
| `slides/` | Slide templates/generators | Keep templates; ignore generated `.pptx` |
| `src/` | Package source | Keep as primary source root |
| `ssot/` | Single-source-of-truth artifacts | Keep curated canonical indexes |
| `staging/` | Staging area | Ignore or archive; avoid tracked scratch space |
| `tests/` | Tests | Keep |
| `tools/` | Tools | Keep, consolidate with root scripts |
| `tools_v2.3/` | Historical/active v2.3 tools | Migrate active tools into `tools/`, archive old copies |
| `tracking_v2.3/` | Historical task tracking | Keep only canonical task JSON if still used |
| `workflows-to-install/` | Workflow activation bundle | Archive after workflows are installed/verified |

## File-type distribution

Exact extension counts could not be computed without a clone. The visible repository strongly skews toward:

- Markdown documentation and status/handover reports (`*.md`).
- Python orchestration, agents, scripts, and toolkit code (`*.py`).
- JSON/YAML configuration, indexes, workflow definitions, and metrics (`*.json`, `*.yaml`, `*.yml`).
- Generated HTML dashboards (`*.html`) under `docs/`.
- Office/generated assets are intentionally discouraged by `.gitignore` (`*.pptx`, `*.pdf`, archives), although at least one `.docx` is visible in the root listing.

## Next exact command for a full clone

```bash
git ls-files -z | perl -0ne 'chomp; print $_,"\0"' | xargs -0 stat --printf '%s\t%n\n'
```
