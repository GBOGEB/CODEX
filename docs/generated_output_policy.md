# Generated Output Policy

This policy defines how CODEX block-library generated outputs are handled.

## Authority rule

YAML and JSON records are the source of truth.

Generated outputs include:

- Markdown previews
- CSV review registers
- Excel review registers
- Word documents
- HTML views
- notebooks

Generated outputs are review views, not the authoritative data store.

## Edit rule

Manual edits to generated outputs must not silently replace SSOT data.

If a reviewer edits a generated output, that edit must become a change request before the SSOT is updated.

## Current MVP outputs

The current MVP can generate:

- `outputs/block_register.csv`
- `outputs/block_library_preview.md`

These files are intentionally not committed in the first MVP unless a future release policy says otherwise.

## Low-risk review sequence

1. Edit YAML SSOT.
2. Run validation.
3. Generate CSV and Markdown preview.
4. Review generated outputs.
5. Convert any manual review changes into SSOT change requests.
6. Re-run validation and rendering.

## Word numbering rule

Do not store visible outline numbers in YAML as authority.

Correct authority:

- `heading_id`
- `level`
- `word_style`
- `sort_order`

The Word template owns visible numbering.
