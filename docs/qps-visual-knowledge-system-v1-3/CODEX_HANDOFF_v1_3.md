# CODEX HANDOFF — v1.3

> **Status: superseded, kept for lineage (2026-10-18).** This v1.3 stream is
> no longer the active slide system. Current: [`docs/qps-slide-system/`](../qps-slide-system/README.md)
> (YAML → `slides/deck_orchestrator.py` → HTML/Markdown, then
> `tools/house_style/qps_post.py` for the corporate PPTX). The HTML, PDF and
> PPTX outputs listed in this directory's manifest are not present in this
> repository; only these three Markdown files are. Per this stream's own
> non-overwrite policy, nothing here is deleted.

## Intent

Additive-only visual knowledge system evolution.

Do NOT:
- overwrite existing decks
- collapse previous versions
- force single-theme convergence

The visual system intentionally preserves:
- multiple engineering aesthetics
- institutional lineage
- review overlays
- recursive/evolutionary development

---

# Current Maturity

## Stable
- HTML navigation structure
- individual deck separation
- Plotly integration direction
- SVG fallback strategy
- YAML object contracts
- render-system philosophy

## Prototype
- SVG graph traversal
- responsive ultra-dense scaling
- HTML → PPTX regeneration
- Office365 export automation
- side-by-side source comparison

---

# Repository Strategy

Recommended structure:

```text
/docs
  /qps-visual-knowledge-system-v1-0b
  /qps-visual-knowledge-system-v1-1
  /qps-visual-knowledge-system-v1-2
  /qps-visual-knowledge-system-v1-3
```

Versions remain:
- parallel
- reviewable
- historically traceable

---

# Long-term Architecture

```yaml
visual_knowledge_system:
  semantic_layer:
  ontology_layer:
  navigation_layer:
  render_layer:
  export_layer:
  review_layer:
  lineage_layer:
```

The system evolves from:
- presentation files

into:
- engineering knowledge surfaces.

---

# Recommended Follow-up PRs

1. SVG node hyperlink system
2. side-by-side source vs curated review mode
3. responsive ultra-dense scaling
4. utilities/control deck expansion
5. Office365 export automation
6. HTML → PPTX regeneration engine
7. static-host/Jekyll deployment
