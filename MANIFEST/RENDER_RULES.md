# A6 Renderer Governance Rules

System: `GBOGEB/CODEX Engineering Publication & Deck Rendering System`

Codename: `ABACUS_RENDER_PIPELINE`

Status: `ALPHA A6 — Renderer Governance Layer`

## Primary rule

Generated outputs are not canonical. The canonical chain is:

1. MASTER YAML
2. MASTER FIGURES
3. MASTER DECISIONS
4. MASTER SPEAKER NOTES
5. USER PPTX as reference/input
6. Generated outputs

## Renderer contract

Every rendered output must be reproducible from SSOT YAML and registered assets.

Required render targets:

- HTML
- PPTX
- PDF
- Markdown
- GitHub Pages
- Speaker Notes
- MASTER Registry
- Executive Snapshot
- Knowledge Cloud

## Semantic card governance

Semantic colors must transform by theme. They must not be produced by naive inversion.

### Warning cards

Light theme:

```yaml
semantic_cards:
  warning:
    light:
      background: "#F5E8A8"
      text: "#2B2111"
```

Dark theme:

```yaml
semantic_cards:
  warning:
    dark:
      background: "#3B2A00"
      border: "#C89B00"
      text: "#FFE9A3"
```

Forbidden in dark mode:

```yaml
dark_mode:
  pastel_cards: true
```

Required:

```yaml
dark_mode:
  pastel_cards: false
```

## Contrast governance

Every semantic card must satisfy contrast validation before release.

Minimum requirements:

- body text: WCAG AA contrast target
- title text: WCAG AA contrast target
- badges and metadata: no white-on-pastel in dark mode
- dark cards use darker semantic backgrounds and warmer pale text

## Typography engine rules

The renderer must enforce:

- heading hierarchy
- adaptive text scaling
- bullet rendering consistency
- semantic emphasis rules
- technical text monospace rendering

Canonical fonts:

```yaml
fonts:
  title:
    family: Aptos
    size: 24
    weight: 700
  section:
    family: Aptos
    size: 18
    weight: 600
  body:
    family: Aptos
    size: 13
  technical:
    family: Consolas
    size: 12
```

## Layout engine rules

The renderer must enforce:

- card auto-height
- whitespace governance
- overflow detection
- landscape slide safety
- asymmetry balancing
- no clipped title bars
- no unreadable overlays

## Navigation engine rules

The renderer must support:

- semantic topic navigation
- local next/previous links
- MASTER figure linking
- PDF anchor support
- slide ID anchors

Every slide requires a stable ID.

## Lineage rules

Every output must trace to:

- source PPTX where applicable
- source slide number where applicable
- MASTER YAML ID
- MASTER figure IDs
- generation timestamp or run ID
- renderer version or phase tag

## CI renderer gates

A6 introduces these future CI checks:

- YAML schema validation
- semantic contrast linting
- required slide ID linting
- missing figure reference detection
- orphan output detection
- dark/light theme snapshot checks
- render smoke tests

## A6 acceptance criteria

A6 is acceptable when:

- dark warning cards are readable
- pastel cards are disabled in dark mode
- MANIFEST files define renderer contracts
- MASTER slide and figure registries exist
- changelog records known issues and next actions
- Codex has an executable task for renderer linting and CI checks
