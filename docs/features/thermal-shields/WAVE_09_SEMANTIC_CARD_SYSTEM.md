# Wave 09 — Semantic Engineering Card System

## Objective

Wave 09 establishes the semantic card runtime layer for the Engineering Deck Convergence Platform.

The system normalizes engineering content into reusable semantic cards while preserving:
- evidence fidelity
- engineering hierarchy
- layout intent
- metadata structure
- visual consistency

## Semantic Card Taxonomy

| Card Type | Purpose |
|---|---|
| EvidenceCard | Photographs and CAD evidence |
| TableCard | Structured metadata and engineering matrices |
| SVGCard | Conceptual engineering abstractions |
| FEACard | Simulation and verification views |
| OCRPreviewCard | Collapsible OCR metadata |
| ActionCard | Decisions and engineering actions |
| CompositeLayout | Multi-semantic engineering slide |

## Layout Runtime

### Dual-Column Architecture

| Left Column | Right Column |
|---|---|
| Structural concept or plot | Metadata tables or engineering blocks |

## Heading System

- exact heading placement
- exact subheading placement
- title-band consistency
- global hierarchy normalization

## Card Runtime Contract

```yaml
card:
  title_band:
    enabled: true
    normalized: true

  body:
    responsive: true
    preserve_spacing: true

  evidence:
    preserve_full_frame: true

  metadata:
    structured: true
```

## Runtime Policies

- cards preserve semantic engineering intent
- OCR never dominates semantic cards
- title bands normalize hierarchy
- engineering metadata remains structured
- responsive layout stability prioritized

## DMAIC Metrics

### DEFINE

| Metric | Value |
|---|---|
| Semantic card architecture stability | 93% |
| Layout hierarchy consistency | 91% |

### MEASURE

| Metric | Target |
|---|---|
| Card consistency | >95% |
| Responsive stability | >92% |
| Metadata extraction quality | >88% |
| Heading normalization | >95% |

### ANALYZE

Detected structural needs:
- mixed semantic engineering slides
- inconsistent hierarchy grouping
- metadata fragmentation
- unstable responsive alignment

### IMPROVE

Implemented direction:
- semantic card taxonomy
- dual-column runtime layout
- title-band normalization
- composite engineering layouts

### CONTROL

Validation controls:
- heading alignment checks
- card spacing validation
- metadata integrity scoring
- responsive layout snapshots
