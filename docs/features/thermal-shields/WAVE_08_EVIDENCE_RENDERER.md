# Wave 08 — Evidence Preservation Renderer

## Objective

Wave 08 establishes the first executable evidence runtime layer of the Engineering Deck Convergence Platform.

The renderer prioritizes:
- implementation photographs
- CAD screenshots
- engineering plots
- process diagrams

as primary engineering evidence.

OCR remains subordinate preview metadata.

## Core Principle

IMAGE > OCR

unless:
- source evidence unreadable
- OCR confidence verified
- evidence retained separately

## Evidence Renderer Components

| Component | Purpose |
|---|---|
| EvidenceCard | High-fidelity engineering evidence block |
| OCRPreviewCard | Collapsible OCR sidecar |
| FidelityValidator | Detect crop/compression loss |
| AlignmentRuntime | Normalize engineering layout |
| ResponsiveImageGrid | Stable responsive evidence rendering |

## Evidence Rendering Contract

```yaml
image_card:
  aspect_ratio: 1:1
  object_fit: contain
  preserve_full_frame: true
  hidden_borders: true
  soft_blend_edges: true
  ocr_sidecar: collapsible
```

## Runtime Policies

- Never crop engineering evidence.
- Preserve full-frame implementation photography.
- OCR may never replace evidence imagery.
- CAD layouts preserve relative geometric positioning.
- Headings remain globally normalized.

## DMAIC Metrics

### DEFINE

| Metric | Value |
|---|---|
| Evidence policy stability | 96% |
| Fidelity governance clarity | 94% |

### MEASURE

| Metric | Target |
|---|---|
| Evidence preservation | >95% |
| Crop loss | <1% |
| OCR suppression | >90% |
| Responsive stability | >92% |

### ANALYZE

Detected risks:
- OCR replacing evidence
- cropped engineering photographs
- raster degradation
- inconsistent responsive scaling

### IMPROVE

Implemented direction:
- square evidence cards
- OCR sidecar suppression
- evidence-first rendering runtime
- responsive evidence layouts

### CONTROL

Validation controls:
- image fidelity checks
- OCR intrusion scoring
- aspect-ratio preservation
- evidence completeness validation
