# GBOGEB Session Integration — 2026-05-22 (Visual Asset Governance)

**Node:** `GBOGEB/session-2026-05-22` · **Plane:** governance (supplemental) · **Status:** DRAFT (for review)

Assimilates the CODEX-side deliverables of the 2026-05-22 session into
`GBOGEB/CODEX` under a non-colliding top-level namespace `integrations/gbogeb_session/`.

## Why this replaces the orphan branch
The session work shares **no git history** with this repository. This branch is
cut from `origin/main`, adds everything under a dedicated namespace, and is a
normal reviewable PR — replacing the earlier unrelated-history approach.

## Role boundary (respected)
Per the federation topology, **CODEX is the governance/supplemental plane, NOT the
runtime single-source-of-truth.** The assets here are canonical *design* sources
(SVGs + validators); the runtime document source of truth remains
`GBOGEB/document-organization-system`. Nothing in this PR promotes CODEX to the
runtime SSOT.

## Contents
| Path | Contents | Tests |
|------|----------|-------|
| `assets_governance/src/` | `asset_validator.py`, `svg_cleaner.py`, `lineage_tracker.py` | 68 ✓ |
| `assets_governance/assets/canonical/` + `compiled/` | 5 engineering SVGs (cryomodule, electrical, facility, P&ID, thermal) × canonical/compiled | — |
| `assets_governance/config/`, `docs/`, `web/` | topology, stakeholder registry, visual data, GBA integration doc, hub | — |
| `orchestration_docs/` | GBC MCP orchestration, cross-repo bridge, integration manifest, exhibit tuples | — |
| `assets_governance/.github/workflows/*.yml.txt` | CI staged as text (App token lacks workflow scope) | — |

## Running the tests in-tree
```bash
cd integrations/gbogeb_session/assets_governance
python -m pytest tests -q      # 68
```
