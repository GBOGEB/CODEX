# ABACUS Bridge Plan for CODEX Block Library

Purpose: define how ABACUS should consume CODEX block-library SSOT after the CODEX MVP stabilizes.

## Boundary

CODEX owns:

- block records
- heading records
- schemas
- render profiles
- generated review views

ABACUS owns:

- DMAIC scoring
- quality gates
- lineage completeness scoring
- runtime evidence scoring
- governance telemetry

## Bridge inputs

Initial ABACUS bridge should read:

- `ssot/blocks/sample_blocks.yaml`
- `ssot/blocks/sample_headings.yaml`
- `ssot/schemas/block.schema.json`
- `ssot/schemas/heading.schema.json`
- `render_profiles/word_template_profile.yaml`

## First ABACUS outputs

Planned follow-up outputs:

- block library quality score
- heading consistency score
- lineage completeness score
- generated-output control score
- release-readiness summary

## Minimum scoring lanes

| Lane | Meaning |
|---|---|
| Architecture maturity | Does the model make sense? |
| Runtime evidence | Do scripts and CI prove it? |
| Lineage completeness | Can artifacts trace to source intent? |
| Render readiness | Can outputs be generated without manual numbering? |
| Governance control | Are edits and generated outputs controlled? |

## First ABACUS follow-up task

Create an ABACUS adapter that reads CODEX block and heading YAML files and produces a quality report without modifying CODEX SSOT.

## Control rule

ABACUS may score CODEX, but CODEX remains the source of truth for block-library records.
