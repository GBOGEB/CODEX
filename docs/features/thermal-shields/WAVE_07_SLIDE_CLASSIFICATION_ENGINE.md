# Wave 07 — Engineering Slide Classification Engine

## Purpose

Wave 07 establishes the first executable semantic layer of the Engineering Deck Convergence Platform.

The objective is not knowledge extraction alone, but classification of engineering visual semantics so that downstream renderers can preserve evidence fidelity and layout intent.

## Supported Slide Archetypes

| Type | Description |
|---|---|
| CAD | CAD screenshots and geometry views |
| PHOTO | Real-world implementation photographs |
| FEA | Thermal/stress simulation outputs |
| PID | Process and instrumentation diagrams |
| TABLE | Structured engineering metadata tables |
| OCR | OCR-dominant text recovery slides |
| MIXED | Composite engineering layouts |

## Semantic Output Contract

```yaml
slide:
  id:
  type:
  confidence:
  evidence_regions:
  table_regions:
  heading_regions:
  annotation_regions:
  ocr_regions:
```

## Renderer Binding

| Slide Type | Runtime Renderer |
|---|---|
| CAD | CADCard |
| PHOTO | EvidenceCard |
| FEA | FEACard |
| PID | SVGCard |
| TABLE | TableCard |
| MIXED | CompositeLayout |

## Evidence Governance Rules

- Photographs remain primary evidence assets.
- OCR is subordinate preview-only metadata.
- CAD layouts preserve alignment and relative positioning.
- Headings are normalized globally.
- Renderer shall preserve engineering intent before textual simplification.

## DMAIC Metrics

### DEFINE

| Metric | Value |
|---|---|
| Renderer philosophy stability | 94% |
| Classification scope definition | 91% |

### MEASURE

| Metric | Target |
|---|---|
| Classification accuracy | >92% |
| Mixed-layout detection | >85% |
| False positive rate | <5% |

### ANALYZE

Detected structural patterns:
- raster-heavy CAD layouts
- evidence photographs
- annotation-dense slides
- dual-column engineering structures
- semantic table blocks

### IMPROVE

Implemented direction:
- semantic slide taxonomy
- renderer binding contracts
- evidence-first governance

### CONTROL

Validation controls:
- OCR suppression checks
- heading lock enforcement
- evidence preservation scoring
- semantic-region validation
