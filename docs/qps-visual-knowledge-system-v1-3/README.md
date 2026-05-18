# QPS Visual Knowledge System v1.3

## Principle

This directory intentionally does NOT overwrite any existing deck structure.

All v1.3 outputs are versioned and additive.

---

# Included Render Targets

## HTML
- integrated visual navigation
- dedicated diagram slides
- embedded diagrams inside slides
- Plotly interactive charts
- SVG fallbacks
- light/dark themes
- graph navigation

## Markdown
- rendered markdown per deck
- YAML-compatible content structure
- future Jekyll integration target

## PDF
- landscape engineering-slide exports
- print-compatible fallbacks

## PPTX
- Office365-compatible export targets
- presentation-first review mode

## YAML
- diagram objects
- plot objects
- render contracts
- navigation contracts

---

# Individual Decks

1. Title and Navigation
2. SBS Graph Navigation
3. Utilities Dense Engineering
4. Controls Dense Engineering
5. Asset Ontology
6. Plots and Diagrams
7. Export Pipeline

---

# Key Additions Compared to v1.1/v1.2

- true diagram-first navigation direction
- embedded + dedicated visual modes
- Plotly interactive layer
- SVG fallback strategy
- separate topic-focused decks
- render contract structure
- Office365 export direction
- PPTX/PDF/Markdown parallel outputs
- responsive scaling strategy
- side-by-side comparison preparation

---

# Non-overwrite Policy

This version:
- does not replace existing decks
- does not delete legacy structures
- does not invalidate prior versions

Instead it:
- extends the visual knowledge system
- adds render-system maturity
- introduces navigation architecture
- preserves recursive/evolutionary workflow


---

# System Framing (Semantic Engineering)

Slides are treated as **semantic engineering artefacts**, not presentation pages.

Canonical architecture:

```
PPTX / PDF / Images
  -> semantic extraction
  -> YAML object layer
  -> HTML engineering surface
  -> multi-render export system
```

Core principles:
- HTML-first
- additive-only versioning
- preserve lineage
- preserve visual nuance
- preserve engineering density
- multiple style families are intentional
- PPTX is an export target

## Version Lineage

Current versions tracked in this stream:
- v1.0b
- v1.1
- v1.2
- v1.3

## Merged PRs

- #56
- #59

## Next Priorities

1. SVG graph traversal
2. side-by-side review mode
3. utilities/control expansion
4. responsive ultra-dense rendering
5. Office365 export automation
6. HTML -> PPTX regeneration
7. static-host deployment
