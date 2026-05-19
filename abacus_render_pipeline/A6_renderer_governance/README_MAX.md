# ABACUS_RENDER_PIPELINE — A6 Renderer Governance Handover

System: Engineering Publication & Deck Rendering System  
Codename: ABACUS_RENDER_PIPELINE

## Primary Objective

Transform USER MASTER PPTX into SSOT YAML, which deterministically generates:

- HTML
- PPTX
- PDF
- Markdown
- GitHub Pages
- Speaker Notes
- MASTER Figure Registry
- Executive Snapshots
- Knowledge Clouds

## Current Maturity

Current state: ALPHA A5  
Status: Functional Prototype  
Next milestone: A6 — Renderer Governance Layer

## A6 Purpose

The bottleneck is no longer content generation. The bottleneck is deterministic rendering quality.

A6 introduces governance for:

- contrast accessibility
- semantic colour transformation
- typography hierarchy
- spacing governance
- card sizing
- navigation semantics
- figure registry traceability
- CI/CD rendering validation

## Critical Rule

Semantic colours must transform by theme, not merely invert.

Dark mode must not use pastel warning cards.

## Canonical Source Hierarchy

1. MASTER YAML
2. MASTER FIGURES
3. MASTER DECISIONS
4. MASTER SPEAKER NOTES
5. USER PPTX as reference/input
6. GENERATED OUTPUTS

Generated outputs are never canonical.
