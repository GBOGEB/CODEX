# Federation Input Template (ABACUS ↔ CODEX)

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
- Missing automation hooks:
  - [ ] Pull lineage/build/deploy state directly from both repos.
  - [ ] Attach CI/CD run URLs and commit SHAs for each cycle row.
  - [ ] Compute and publish PCA/DMAIC/ANOVA outputs instead of manual summaries.
- TODO owner: TBD
- TODO due date (UTC): TBD
