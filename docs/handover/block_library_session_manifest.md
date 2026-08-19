# Block Library Session Manifest

Active PR: GBOGEB/CODEX#239
Branch: feature-block-library-ssot-v1
Status: draft implementation PR

## Purpose

This file records the session lineage and implementation state for the CODEX and ABACUS reusable block-library workstream.

## Conversation lineage

1. Reusable code storage: use Markdown for readable blocks and YAML or JSON for authority.
2. Runtime targets: support VS Code, Google Colab, Jupyter, Python CLI and GitHub Actions.
3. Word template mapping: preserve stable IDs and let the Word template generate outline numbering.
4. Repository split: CODEX owns SSOT and generated views. ABACUS owns validation and quality scoring.
5. Scoring: separate architecture maturity from runtime evidence.
6. PR creation: continue PR 239 rather than creating duplicate PRs.
7. Proceeding implementation: add CSV export, Markdown preview, Word render profile and CI validation.

## Artifact manifest

- .github/workflows/validate_blocks.yml
- docs/adr/CODEX_ABACUS_BLOCK_LIBRARY_DMAIC_ITER002.md
- docs/handover/block_library_session_manifest.md
- render_profiles/word_template_profile.yaml
- scripts/export_blocks_to_csv.py
- scripts/render_markdown_preview.py
- scripts/validate_blocks.py
- ssot/blocks/sample_blocks.yaml
- ssot/schemas/block.schema.json

## Implementation waves

- Wave 0: Architecture baseline started.
- Wave 1: SSOT schema seed started.
- Wave 2: Runtime validator MVP started.
- Wave 3: CSV register export started.
- Wave 4: CI validation gate started.
- Wave 5: Markdown preview started.
- Wave 6: Word render profile started.
- Wave 7: ABACUS quality federation not started.

## Next three moves

1. Review CI results and fix any path or dependency issue.
2. Add README usage notes for validator, CSV exporter and Markdown preview renderer.
3. Add heading schema and heading-level validation.

## Control rules

- YAML and JSON are the source of truth.
- Markdown, CSV, Excel, Word and HTML are generated views.
- Do not hard-code Word outline numbers.
- Preserve block_id and heading_id.
- Word numbering must come from dotm Heading styles.
