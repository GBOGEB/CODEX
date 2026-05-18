# PR-H2 Generated Overlay Pipeline

## Purpose

PR-H2 turns the PR-H visualization scaffolds into a generated data pipeline.

It builds on PR-H and focuses on:

- repeatable JSON regeneration,
- Plotly trace export,
- GitHub Pages artifact refresh,
- CI-safe fallback generation,
- future CoolProp runtime enrichment.

## Parent Branch

```text
pr-h-thermo-visual-overlays
```

## Topic Branch

```text
pr-h2-generated-overlay-pipeline
```

## Parent Rules

1. Do not require CoolProp, REFPROP, or HEPAK in CI.
2. Always keep deterministic fallback generation available.
3. Generated artifacts must be GitHub Pages-visible.
4. Visualization schemas should evolve additively where possible.
5. H2 may depend on H until H is merged; rebase H2 onto main after H lands.

## Initial Scope

- add generated artifact manifest,
- expose refresh command wrapper,
- export Plotly trace JSON,
- add CI-safe pipeline tests,
- document Pages refresh workflow.

## Deferred

- real CoolProp saturation data,
- executable backend T-s trajectories,
- REFPROP canonical overlays,
- HEPAK 2 K helium overlays,
- publication PNG rendering.
