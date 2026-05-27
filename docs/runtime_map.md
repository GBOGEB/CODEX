---
title: Runtime Governance Map
---

# Runtime Governance Map

## State Model

```text
proposal -> triage -> assigned -> execution -> validation -> promoted -> archived
                               \-> rolled_back -> triage
```

## Agentic Process

1. GPT chat agent receives intent and constraints.
2. ABACUS assigns governance state and route.
3. MCP Sweep evaluates capability and dependency fit.
4. CODEX workers execute patches/automation.
5. Validation gates run.
6. MCP Mop resolves drift and finalizes closeout.
7. ABACUS promotes or rolls back.

## Governance Rendering Defaults

- Markdown documentation under `docs/` rendered by Jekyll defaults in `_config.yml`.
- Diagram outputs are expected to prefer SVG and Plotly exports.
- RTM contract remains locked; only generic topic references are added.
