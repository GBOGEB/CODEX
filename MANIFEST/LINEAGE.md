# LINEAGE

## Purpose

Define reproducible lineage requirements for renderer outputs and governance artifacts in `ABACUS_RENDER_PIPELINE`.

## Required lineage fields per render

- `run_id`
- `renderer_version`
- `theme`
- `source_master_yaml_id`
- `source_slide_id` (when applicable)
- `source_figure_ids` (when applicable)
- `output_targets`
- `generated_at_utc`

## Lineage policy

- Generated HTML/PPTX/PDF artifacts are non-canonical derivatives.
- Canonical lineage starts from SSOT artifacts (MASTER YAML + registries).
- Render validation and linting must be traceable to this manifest lineage contract.
