# RENDER RULES

## Purpose

Renderer governance for the ABACUS_RENDER_PIPELINE.

This document defines deterministic rendering contracts for:

- HTML
- PPTX
- PDF
- Markdown
- GitHub Pages
- snapshot views

Generated outputs are never canonical.

Canonical source hierarchy:

1. MASTER YAML
2. MASTER FIGURES
3. MASTER DECISIONS
4. MASTER SPEAKER NOTES
5. USER PPTX
6. GENERATED OUTPUTS

---

# Theme Governance

Theme transforms are semantic.

Dark mode MUST NOT simply invert light-mode palettes.

Semantic cards must define explicit light and dark variants.

Example:

```yaml
semantic_cards:
  warning:
    light:
      background: '#F5E8A8'
      text: '#2B2111'
    dark:
      background: '#3B2A00'
      border: '#C89B00'
      text: '#FFE9A3'
```

---

# Accessibility

Renderer targets WCAG-compliant contrast behavior.

Pastel cards in dark mode are prohibited.

Contrast rules:

- semantic intent must survive theme transform
- text contrast must remain readable
- borders must remain visible in PDF export
- warning cards must use warm-dark backgrounds in dark mode

---

# Typography Governance

Fonts:

| Role | Family |
|---|---|
| title | Aptos |
| section | Aptos |
| body | Aptos |
| technical | Consolas |

Renderer responsibilities:

- adaptive heading scaling
- overflow prevention
- semantic emphasis preservation
- deterministic bullet spacing

---

# Layout Governance

Renderer must implement:

- card auto-height
- whitespace balancing
- overflow detection
- semantic asymmetry balancing
- stable navigation placement

---

# Stable IDs

Every slide requires immutable IDs.

Example:

```yaml
slide_id: MSLIDE_EXEC_INFOCARD_01
```

Stable IDs are required for:

- lineage
- figure references
- snapshots
- PDF anchors
- changelog traceability
- speaker-note traceability

---

# Validation Direction

Future CI rendering validation should include:

- contrast linting
- overflow linting
- spacing linting
- snapshot regression checks
- navigation validation
- theme transform checks
