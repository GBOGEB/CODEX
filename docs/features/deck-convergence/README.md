# Engineering Deck Convergence Engine

This feature defines the generalized method for reproducing engineering slide decks as structured HTML.

Thermal Shields is reference dataset 001. Additional thematic decks can be added later as dataset 002, dataset 003, and so on.

## Primary purpose

The goal is not only to capture domain knowledge. The core goal is slide deck reproduction and HTML convergence as a reusable engineering technique.

## Core outputs

- high fidelity square evidence image cards
- optional OCR preview sidecars
- CAD and photo alignment rules
- heading and subheading placement locks
- dual column engineering layouts
- semantic cards with title bands
- SVG abstraction layer for conceptual reproduction
- YAML 1.2 compatible contracts
- Jekyll ready static site outputs
- DMAIC and maturity hooks for ABACUS

## Dataset roles

| Dataset | Status | Role |
|---|---|---|
| thermal_shields_001 | active | baseline reference deck |
| deck_002 | waiting | future diversity input |
| deck_003 | waiting | future diversity input |

## Repository split

CODEX owns the renderer, parser, layout contracts, and HTML output patterns.

ABACUS owns DMAIC governance, maturity metrics, KPI tracking, lineage, and deployment readiness scoring.

## Functional block split for CODEX and ABACUS

The first YAML/CSS orchestration target is the MINERVA QPS procurement cybersecurity appendix deck. It demonstrates the intended repository split:

| Block | CODEX responsibility | ABACUS responsibility |
|---|---|---|
| Content ingress | Validate `deck_content.yaml`, normalize slide ids, preserve RTM/corrigendum fields | Score source completeness and fixed/locked status |
| Presentation contract | Apply `deck_style.css` to deterministic HTML review output | Check contrast/style invariants against maturity gates |
| Conversion handoff | Emit Pandoc-ready Markdown for PPTX/PDF generation | Track generated artifact lineage and checksums |
| Manifest | Write deterministic JSON artifact manifest | Consume manifest for governance, DMAIC, and release readiness |

This keeps the release package updateable by changing YAML content without re-designing the visual system.
