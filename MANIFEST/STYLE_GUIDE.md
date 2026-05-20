# STYLE GUIDE

## System

GBOGEB/CODEX

Codename:

ABACUS_RENDER_PIPELINE

## Renderer Principle

Semantic colors must transform by theme.

They must not merely invert.

## Contrast Governance

### Incorrect Pattern

- pastel yellow background
- white text
- low contrast in dark mode

### Correct Pattern

```yaml
warning:
  dark:
    background: "#3B2A00"
    border: "#C89B00"
    text: "#FFE9A3"
```

## Theme Governance

### Light Theme

```yaml
theme_light:
  canvas: "#F4F2EE"
  title_bar: "#5B2E91"
  title_text: "#FFFFFF"
```

### Dark Theme

```yaml
theme_dark:
  canvas: "#181421"
  card: "#241D33"
  text: "#F5F2FF"
```

## Typography Governance

### Title
- Aptos
- 24pt
- weight 700

### Section
- Aptos
- 18pt
- weight 600

### Body
- Aptos
- 13pt

### Technical
- Consolas
- 12pt

## Renderer Constraints

- Generated outputs are never canonical.
- MASTER YAML is the SSOT.
- Every slide requires a stable ID.
- Every render writes lineage metadata.
- Every render writes changelog metadata.
