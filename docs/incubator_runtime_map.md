# Incubator Runtime Map

This page describes W000/W001 tuple ingress flow for the INCUBATOR layer.

## Flow

1. Author tuple YAML records in `/incubator` using the naming convention.
2. Validate and parse tuples with `python scripts/parse_chat_tuple.py`.
3. Build the Markdown index with `python scripts/build_incubator_index.py`.
4. Extract simple theme counts with `python scripts/extract_themes.py`.
5. Export runtime for portability with `python scripts/export_incubator_runtime.py`.
6. Stage portable artifacts for downstream pipelines from `outputs/incubator_export/`.

## Mapping sources

- Category map: `maps/category_map.yml`
- Theme map: `maps/theme_map.yml`
- Repo ingress map: `maps/repo_ingress_map.yml`

## ABACUS Bridge Integration

INCUBATOR follows the bridge architecture documented in:
- `docs/ALPHA_BRIDGE_ABACUS_CODEX.md` — Overall CODEX/ABACUS strategic boundary
- `docs/INCUBATOR_ABACUS_BRIDGE.md` — INCUBATOR-specific integration points

See ABACUS bridge doc for category/theme alignment with DMAIC orchestration.

## Wave Status

- **W000**: complete (naming + schema + seeded tuple file)
- **W001**: complete (parser + markdown index generation + CI validation + tests)
- **W002**: planned (DMAIC phase mapping + ABACUS bridge activation)
- **W003**: planned (Plotly dashboards + timeline visualization)

## Governance

- **CI Validation**: `.github/workflows/ci.yml` runs `scripts/parse_chat_tuple.py`
- **Portable Utility**: `scripts/export_incubator_runtime.py --output-dir <path>` for bridge handoff bundles
- **Test Coverage**: `tests/incubator/` pytest suite
- **Semantic Invariant**: INV-011 in `semantic_substrate/invariants.yaml`
- **Wave Tracking**: `MANIFEST/WAVE_PROGRESSION.yaml` incubator_waves section
