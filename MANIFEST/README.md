# ABACUS_RENDER_PIPELINE

## System Name

GBOGEB/CODEX Engineering Publication & Deck Rendering System

Codename:

```text
ABACUS_RENDER_PIPELINE
```

## Primary Objective

Transform a USER MASTER PPTX into a single-source-of-truth YAML model that deterministically generates:

- HTML,
- PPTX,
- PDF,
- Markdown,
- GitHub Pages,
- speaker notes,
- MASTER figure registry,
- executive snapshots,
- knowledge clouds.

## Current Maturity

```text
ALPHA A5 -> A6 transition
```

A5 proved rendering capability.

A6 introduces renderer governance, linting, lineage, contrast rules, and deterministic rendering contracts.

## Canonical Source Hierarchy

1. MASTER YAML
2. MASTER FIGURES
3. MASTER DECISIONS
4. MASTER SPEAKER NOTES
5. USER PPTX as reference input
6. GENERATED OUTPUTS

Generated outputs are never canonical.

## A6 Objective

A6 focuses on deterministic renderer quality:

- semantic theme governance,
- contrast governance,
- layout governance,
- typography governance,
- renderer contracts,
- lineage and manifesting,
- CI/CD readiness.

## A6 Manifest Files

- `README.md`
- `RENDER_RULES.md`
- `STYLE_GUIDE.md`
- `CHANGELOG.md`
