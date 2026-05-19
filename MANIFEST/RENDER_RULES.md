# RENDER RULES

## Renderer Governance Layer

A6 introduces deterministic renderer governance.

## Mandatory Engines

### Typography Engine

Responsibilities:
- heading hierarchy
- adaptive scaling
- semantic emphasis
- bullet normalization

### Layout Engine

Responsibilities:
- whitespace governance
- overflow detection
- card auto-height
- asymmetry balancing

### Navigation Engine

Responsibilities:
- semantic topic navigation
- next/previous traversal
- figure linking
- PDF anchor support

### Contrast Engine

Responsibilities:
- WCAG validation
- adaptive theme palettes
- semantic card transformation
- dark/light governance

## Canonical Source Hierarchy

1. MASTER YAML
2. MASTER FIGURES
3. MASTER DECISIONS
4. MASTER SPEAKER NOTES
5. USER PPTX
6. GENERATED OUTPUTS

## Renderer Invariants

- generated outputs are non-canonical
- every slide requires stable ID
- every render must be reproducible
- every render must emit lineage metadata
- every render must emit changelog metadata
- semantic surfaces must pass contrast validation

## Current A6 Priority

The most critical renderer-governance issue currently identified:

- warning card contrast failure in dark mode

Target correction:

```yaml
warning:
  dark:
    background: "#4A3110"
    text: "#FFE9A3"
```
