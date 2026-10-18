# Deck Manifest — v1.3

> **Status: superseded, kept for lineage (2026-10-18).** This v1.3 stream is
> no longer the active slide system. Current: [`docs/qps-slide-system/`](../qps-slide-system/README.md)
> (YAML → `slides/deck_orchestrator.py` → HTML/Markdown, then
> `tools/house_style/qps_post.py` for the corporate PPTX). The HTML, PDF and
> PPTX outputs listed in this directory's manifest are not present in this
> repository; only these three Markdown files are. Per this stream's own
> non-overwrite policy, nothing here is deleted.

| Deck ID | Deck Name | HTML | MD | PDF | PPTX | YAML | Status |
|---|---|---|---|---|---|---|---|
| 00 | Title and Navigation | yes | yes | yes | yes | partial | active |
| 01 | SBS Graph Navigation | yes | yes | yes | yes | yes | active |
| 02 | Utilities Dense Engineering | yes | yes | yes | yes | partial | active |
| 03 | Controls Dense Engineering | yes | yes | yes | yes | partial | active |
| 04 | Asset Ontology | yes | yes | yes | yes | yes | active |
| 05 | Plots and Diagrams | yes | yes | yes | yes | yes | active |
| 06 | Export Pipeline | yes | yes | yes | yes | yes | planning |

---

# Navigation Philosophy

## Integrated Mode
Diagrams and plots embedded directly into engineering slides.

## Dedicated Mode
Diagrams and plots also exist as:
- standalone slides
- graph navigation objects
- SVG render targets
- Plotly render targets

---

# Planned Next Iteration

## SBS
- clickable SVG node graph
- hierarchy traversal
- interface-link overlays

## Utilities
- denser cooling/HVAC/RCW/PCW slides
- assumption traceability
- utility interaction matrices

## Controls
- I/O candidate grouping
- subsystem interaction maps
- readiness and inhibit matrices
- mode interaction navigation

## Export
- HTML → PDF landscape stabilization
- HTML → PPTX regeneration
- Office365 review copies
- Jekyll/static-host rendering

---

# Visual Strategy

The system preserves:
- corporate purple authority
- blue-white engineering precision
- green SBS hierarchy
- apricot operational overlays
- yellow/red critique overlays

without forcing a single diluted theme.
