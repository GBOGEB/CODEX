# Render Governance Rules (A6)

## Canonical Source Rule
- **Generated outputs are never canonical**.
- Canonical content must remain in source YAML/MD + figure registry.
- Manual edits to generated PPTX/PDF/HTML are prohibited.

## Determinism Rules
- Given identical canonical input + renderer version + theme token set, output must be byte-stable where format allows.
- All non-deterministic metadata (timestamps, random IDs) must be normalized.
- Render jobs must emit lineage records.

## Governance Gates
- Render passes only if all lints pass:
  - no_overflow
  - no_low_contrast
  - stable_heading_hierarchy
  - figure_reference_required
  - semantic_card_required
  - slide_id_required

## Exception Process
- Any override requires:
  1. reason
  2. approver
  3. expiry date
  4. linked issue
