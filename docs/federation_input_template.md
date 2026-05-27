# Federation Input Template (ABACUS ↔ CODEX)

> **⚠️ STATUS**: This is a manual input template. Automated ingestion not yet implemented.  
> **📊 Progress**: See [FEDERATION_BRIDGE_PROGRESS.md](FEDERATION_BRIDGE_PROGRESS.md) for development status.  
> **🔗 PR**: [codex/implement-ci/cd-pipeline-for-repo-build-and-deploy](https://github.com/GBOGEB/CODEX/tree/codex/implement-ci/cd-pipeline-for-repo-build-and-deploy)

## 1) Scope
- Upstream repo:
- Downstream repo:
- Bridge objective:
- Cycle id:
- Cycle start/end (UTC):

## 2) Lineage + Build + Deploy
- Source lineage chain:
- Build commands:
- Deploy target (GitHub Pages / Actions / Other):
- CI workflow files:

## 3) Progress: Claimed vs Actual
| Lane | Claimed | Actual | Evidence |
|---|---:|---:|---|
| Lineage |  |  |  |
| Build |  |  |  |
| Deploy |  |  |  |
| CI/CD |  |  |  |

## 4) Wave Tracking Stats
- PCA summary:
- DMAIC stage + blockers:
- ANOVA/covariance observations:

## 5) Output Conversion
- Maturity:
- Orchestration:
- Agents:
- MCP protocols:
- Topography:

## 6) Repo ASCII Diagram
```text
[ABACUS main] ---- bridge APIs ---- [CODEX main]
      |                                 |
  upstream                         downstream
      \---- shared lineage + CI/CD ----/
```

## 7) YAML Glossary Linkage
- See `MANIFEST/FEDERATION_GLOSSARY.yaml`.

## 8) Missing Buildout Notes / TODO

### Automated Ingestion (⚠️ Not Started - HIGH Priority)
- [ ] Pull lineage/build/deploy state directly from both repos.
- [ ] Attach CI/CD run URLs and commit SHAs for each cycle row.
- [ ] Compute and publish PCA/DMAIC/ANOVA outputs instead of manual summaries.

### Current Limitations
- **Manual data entry**: Users must fill all fields manually (no GitHub API integration)
- **No evidence linking**: Progress percentages cannot be verified automatically
- **Static analytics**: Wave stats are descriptive text, not computed from data
- **No CI/CD triggers**: Dashboard updates require manual commits

### Development Tracking
- **TODO owner**: TBD
- **TODO due date (UTC)**: TBD
- **Estimated effort**: 2-3 days (automated ingestion) + 1-2 days (evidence linking) + 3-5 days (analytics)
- **Blockers**: None currently identified
- **Dependencies**: GitHub API token, read access to ABACUS/CODEX repos

### Related Documentation
- 📊 [FEDERATION_BRIDGE_PROGRESS.md](FEDERATION_BRIDGE_PROGRESS.md) - Comprehensive progress tracker
- 🏠 [federation_bridge_dashboard.html](federation_bridge_dashboard.html) - Visual dashboard
- 📖 [MANIFEST/FEDERATION_GLOSSARY.yaml](../MANIFEST/FEDERATION_GLOSSARY.yaml) - Terminology

### Recent Commits
- `e85ab02` (2026-05-24): Clarify TODO owner and due date placeholders as TBD
- `1d8d8b2` (2026-05-24): Register federation HTML pages and document stub TODO gaps
