# Artefact Index — QPS Visual Knowledge System

## Canonical local artefacts produced during the session

### v1.2
`qps_visual_knowledge_system_v1_2.zip`

Focus:
- embedded diagrams in HTML slides
- dedicated diagram slides
- Plotly gallery direction
- SVG fallbacks
- diagram/table indexes
- visual QA

### v1.4
`qps_svg_graph_navigation_mvp_v1_4.zip`

Focus:
- clickable SVG graph MVP
- YAML node registry
- node pages
- side-by-side review shell
- responsive density modes

### v1.5
`qps_graph_lineage_binding_v1_5.zip`

Focus:
- graph → deck bindings
- graph → plot bindings
- graph → table bindings
- node pages
- source-lineage registry contract
- source-vs-curated comparison model
- dense Utilities / Controls / Naming / Asset binding targets

### Session handover
`QPS_SESSION_HANDOVER_v1_5.md`

Focus:
- intended-vs-actual acceptance review
- golden thread
- open gaps
- v1.6 execution contract

## Important boundary

The repo handover does not attempt to commit generated binary packages or user source decks in this PR. It freezes the engineering intent, acceptance state, and next execution contract so the next session/Codex run can ingest artefacts additively without overwriting prior content.

## Repository milestones

- PR #56 — staged implementation architecture
- PR #59 — additive deck/render architecture

## Canonical next implementation path

`docs/qps-source-bound-dense-decks-v1-6/`

## Non-overwrite rule

Earlier versions remain available for:
- lineage
- comparative review
- regression analysis
- visual provenance

No previous deck/version should be silently replaced by v1.6.
