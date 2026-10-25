# GBOGEB/CODEX (GBC)

> **Visual Asset Governance Layer** for engineering diagrams, schematics, and SVG assets.
>
> *Canonical source — Generated outputs are NEVER canonical.*

## Overview

GBOGEB/CODEX is the **design source** complement to [GBOGEB/ABACUS](https://github.com/gbogeb/abacus) (GBA). While GBA handles governance, validation, and publication, GBC manages the **visual assets** consumed by GBA's HMI dashboards, presentations, and technical reports.

### Core Capabilities

| Capability | Engine | Description |
|-----------|--------|-------------|
| **Asset Validation** | `asset_validator.py` | SHA256 hashing, format checks, .mock sidecar creation |
| **SVG Optimization** | `svg_cleaner.py` | Editor cleanup, viewBox normalization, ID injection |
| **Lineage Tracking** | `lineage_tracker.py` | Manifest management, hash verification, version history |
| **Visual Gallery** | `web/index.html` | Asset preview, download links, topology display |
| **CI/CD Pipeline** | GitHub Actions | Automated validation, cleaning, archive generation, Pages deployment |

### Hub & Downloads

| Resource | Path | Description |
|----------|------|-------------|
| 🖼️ Visual Gallery | [`web/index.html`](web/index.html) | Browse and download all visual assets |
| 📦 Asset Bundle | `gbc_asset_bundle.tar.gz` | Compiled SVGs + configs + manifest |
| 🗺️ Knowledge Topology | [`config/knowledge_topology.json`](config/knowledge_topology.json) | Cross-repo node/edge graph |
| 📋 Lineage Manifest | [`lineage_manifest.json`](lineage_manifest.json) | SHA256 asset registry |
| 🎨 Visual Data | [`config/visual_data.yaml`](config/visual_data.yaml) | Asset catalog + theme tokens |

## Quick Start

### Prerequisites

- Python 3.11+
- PyYAML (`pip install pyyaml`)

### Setup

```bash
git clone https://github.com/gbogeb/codex.git
cd codex
pip install pyyaml pytest
```

### Validate Assets

```bash
# Validate all canonical assets
python src/asset_validator.py --input-dir assets/canonical/

# Validate a single file
python src/asset_validator.py --verify assets/canonical/cryomodule_schematic.svg
```

### Clean & Optimize SVGs

```bash
python src/svg_cleaner.py --input-dir assets/canonical/ --output-dir assets/compiled/ --prefix gbc
```

### Track Lineage

```bash
# Add asset to manifest
python src/lineage_tracker.py --add assets/canonical/cryomodule_schematic.svg --category svg_diagram

# View status
python src/lineage_tracker.py --status

# Validate manifest integrity
python src/lineage_tracker.py --validate

# Verify file hashes
python src/lineage_tracker.py --verify-hashes
```

### Run Tests

```bash
python -m pytest tests/ -v
```

### View Gallery

Open `web/index.html` in any modern browser — no server required.

## Repository Structure

```
gbogeb_codex/
├── .github/
│   └── workflows/
│       ├── asset-ingestion.yml        ← asset validation + SVG cleaning
│       └── archive-deploy.yml         ← bundle generation + GitHub Pages
├── assets/
│   ├── canonical/                     ← master source SVGs (never auto-modified)
│   │   ├── cryomodule_schematic.svg
│   │   └── facility_layout.svg
│   └── compiled/                      ← optimized SVGs (auto-generated)
│       ├── cryomodule_schematic.svg
│       └── facility_layout.svg
├── config/
│   ├── knowledge_topology.json        ← cross-repo GBC↔GBA node/edge graph
│   ├── stakeholder_registry.yaml      ← distribution tags and formats
│   └── visual_data.yaml               ← asset catalog + theme tokens
├── docs/
│   ├── GBA_INTEGRATION.md             ← how GBC integrates with GBA
│   └── ASSET_WORKFLOW.md              ← end-to-end asset workflow guide
├── src/
│   ├── asset_validator.py             ← SHA256 hashing, format validation, .mock creation
│   ├── svg_cleaner.py                 ← SVG optimization, ID injection, cleanup
│   └── lineage_tracker.py             ← manifest CRUD, hash verification, reporting
├── tests/
│   ├── test_asset_validator.py        ← 25 tests
│   ├── test_svg_cleaner.py            ← 18 tests
│   └── test_lineage_tracker.py        ← 16 tests (+ canonical asset integration tests)
├── web/
│   └── index.html                     ← visual asset gallery hub
├── lineage_manifest.json              ← SHA256 registry of all tracked assets
└── README.md                          ← this file
```

## Cross-Repository Architecture

```
┌────────────── GBC (CODEX) ──────────────┐   ┌────────────── GBA (ABACUS) ────────────┐
│                                          │   │                                         │
│  assets/canonical/ ──── consumed_by ───►│──►│ HMI Dashboard (SVG diagrams)            │
│  config/visual_data.yaml ── extends ──►│──►│ SEMANTIC_THEME.yaml (theme tokens)      │
│  lineage_manifest.json ──── feeds ────►│──►│ _data/lineage_manifest.json (lineage)   │
│  src/asset_validator.py ── mirrors ───►│──►│ engines/verification_hook.py (pattern)   │
│  web/index.html ────── links_to ──────►│──►│ web/index.html (GBA hub)                │
│                                          │   │                                         │
│  Knowledge Topology: 7 nodes, 6 edges   │   │  Knowledge Topology: 9 referenced nodes │
└──────────────────────────────────────────┘   └─────────────────────────────────────────┘
```

## Visual Assets

### Cryomodule Schematic (`GBC-ASSET-001`)

Cross-sectional view of a superconducting RF cryomodule assembly showing:
- Vacuum vessel (300 K outer shell)
- Thermal shield (80 K, MLI-wrapped)
- Helium vessel (2 K, He-II superfluid)
- SRF cavity string (3 × 9-cell elliptical)
- Beam pipe, power couplers, support posts

**Consumed by:** GBA HMI Dashboard, GBA Presentation Slide 3

### Facility Layout (`GBC-ASSET-002`)

Plan-view layout of the European Spallation Source linear accelerator showing:
- Ion source → RFQ → DTL → Spoke → Medium-β → High-β → HEBT + Target
- Cryoplant and helium distribution connections
- Energy progression: 75 keV → 2000 MeV
- 23 cryomodules across 3 families

**Consumed by:** GBA Presentation Slide 1, GBA Technical Report

## CI/CD Pipelines

| Workflow | Trigger | Jobs |
|----------|---------|------|
| **Asset Ingestion** | Push/PR to `assets/canonical/` | Validate → Clean SVGs → Update lineage |
| **Archive & Deploy** | Push to `main` | Build bundle → Deploy gallery to GitHub Pages |

## GBA Integration

See [`docs/GBA_INTEGRATION.md`](docs/GBA_INTEGRATION.md) for the full integration guide.

Key integration points:
1. **Asset Transfer:** `assets/compiled/` → GBA `Input_Master/`
2. **Theme Tokens:** `visual_data.yaml` extends GBA `SEMANTIC_THEME.yaml`
3. **Lineage Chain:** GBC manifest → GBA manifest (cross-repo traceability)
4. **Knowledge Topology:** Shared node/edge graph across both repos

## License

Part of the GBOGEB ecosystem. See project governance for terms.



---

## 🔌 MCP Server Integration

This repository is connected to the **GBOGEB MCP Server** — a [Model Context Protocol](https://modelcontextprotocol.io/) server providing AI assistants with unified access to the GBOGEB knowledge topology, visual assets, and lineage tracking across GBA and GBC.

### Key MCP Tools for GBC

| Tool | GBC Relevance |
|---|---|
| `get_topology()` | Shows all 7 GBC nodes and cross-repo edges to GBA |
| `get_asset_lineage(id)` | Full SHA256 provenance for GBC SVG assets |
| `list_assets()` | Complete inventory of tracked SVGs from lineage manifest |
| `search_engineering_data(q)` | Searches visual_data.yaml and lineage_manifest.json |
| `query_node("GBC-ASSET-001")` | Cryomodule schematic details with GBA consumers |

### Setup

```bash
cd /home/ubuntu/gbogeb_mcp_server
pip install -e ".[dev]"
gbogeb-mcp  # starts the MCP server (stdio transport)
```

See [`gbogeb_mcp_server/README.md`](/home/ubuntu/gbogeb_mcp_server/README.md) for full documentation.
