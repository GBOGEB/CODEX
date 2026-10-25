# GBA Integration Guide

> How GBOGEB/CODEX (GBC) integrates with GBOGEB/ABACUS (GBA)

## Overview

GBC serves as the **visual asset governance layer** — the canonical source for engineering
diagrams, schematics, and SVG assets. GBA is the **publication governance engine** that
consumes these assets for rendering in dashboards, reports, and presentations.

```
┌──────────── GBC (CODEX) ──────────────┐     ┌──────────── GBA (ABACUS) ─────────┐
│                                        │     │                                    │
│  assets/canonical/ ──────────────────►│────►│ Input_Master/                      │
│  (SVG, PNG, DrawIO sources)           │     │ (verification_hook.py processes)   │
│                                        │     │                                    │
│  config/visual_data.yaml ────────────►│────►│ engines/SEMANTIC_THEME.yaml        │
│  (theme tokens, asset catalog)        │     │ (extends theme tokens)             │
│                                        │     │                                    │
│  lineage_manifest.json ──────────────►│────►│ _data/lineage_manifest.json        │
│  (SHA256 tracking)                    │     │ (cross-repo lineage)               │
│                                        │     │                                    │
│  config/knowledge_topology.json ─────►│────►│ config/knowledge_topology.json     │
│  (node/edge graph)                    │     │ (shared topology)                  │
│                                        │     │                                    │
└────────────────────────────────────────┘     └────────────────────────────────────┘
```

## Integration Points

### 1. Asset Transfer Pipeline

```bash
# 1. Export compiled SVGs from GBC
cd gbogeb_codex
python src/svg_cleaner.py --input-dir assets/canonical/ --output-dir assets/compiled/

# 2. Copy to GBA Input_Master
cp assets/compiled/*.svg ../gbogeb_abacus/Input_Master/

# 3. Run GBA verification hook
cd ../gbogeb_abacus
python engines/verification_hook.py --input-dir Input_Master/ --data-dir _data/
```

### 2. Knowledge Topology

Both repositories maintain `config/knowledge_topology.json` files that reference each other:

| GBC Node | Relation | GBA Node |
|----------|----------|----------|
| `GBC-ASSET-001` (cryomodule.svg) | `consumed_by` | `GBA-HMI-001` (HMI Dashboard) |
| `GBC-ASSET-002` (facility_layout.svg) | `referenced_in` | `GBA-REPORT-001` (Tech Report) |
| `GBC-ENGINE-001` (asset_validator.py) | `mirrors` | `GBA-ENGINE-HOOK` (verification_hook.py) |
| `GBC-ENGINE-003` (lineage_tracker.py) | `feeds` | `GBA-LINEAGE-001` (lineage_manifest.json) |
| `GBC-CONFIG-001` (visual_data.yaml) | `extends` | `GBA-THEME-001` (SEMANTIC_THEME.yaml) |

### 3. Theme Token Mapping

GBC's `visual_data.yaml` defines diagram-specific theme tokens that extend GBA's semantic theme:

```yaml
# GBC visual_data.yaml
theme_tokens:
  diagram_stroke: "var(--color-primary)"      # → GBA SEMANTIC_THEME primary
  diagram_fill_surface: "var(--color-surface)" # → GBA SEMANTIC_THEME surface
  status_nominal: "var(--color-success)"       # → GBA SEMANTIC_THEME success
```

### 4. Lineage Continuity

GBC's `lineage_manifest.json` and GBA's `_data/lineage_manifest.json` form a
**cross-repository lineage chain**:

```
GBC: canonical SVG → sha256 → GBC manifest
                              ↓
GBA: Input_Master/ → verification_hook → GBA manifest → rendered output
```

### 5. Archive Bundle

GBC generates `gbc_asset_bundle.tar.gz` containing:
- Compiled/optimized SVGs
- Visual data registry
- Knowledge topology
- Stakeholder registry
- Lineage manifest

This bundle can be consumed directly by GBA's CI/CD pipeline.

## Validation Checklist

- [ ] All SVGs in `assets/canonical/` pass `asset_validator.py`
- [ ] `lineage_manifest.json` is valid (`lineage_tracker.py --validate`)
- [ ] SHA256 hashes match on-disk files (`lineage_tracker.py --verify-hashes`)
- [ ] `knowledge_topology.json` nodes have matching GBA references
- [ ] Theme tokens in `visual_data.yaml` map to GBA `SEMANTIC_THEME.yaml`
- [ ] CI/CD pipelines complete without errors
