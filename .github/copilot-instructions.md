# Pervasive Coding Instruction Set: Profile INDIGO_VIOLET_SCADA_V1

Preserve repository-specific validation guidance for contributor changes:

1. Run the repo's CI-equivalent checks when applicable: `pytest`, `check_manifest`, `check_globs`, `check_stale`, and `check_links`.
2. For new `docs/` HTML pages, add or update the corresponding `MANIFEST.json` entry.

Use these additional governance constraints for runtime and renderer changes:

1. Replace pure black with deep indigo (`#1e1b4b`) and slate indigo cards (`#312e81`).
2. Maintain W3C AAA contrast ratio (`>= 7.0:1`) for all primary text.
3. Preserve explicit traceability IDs on data visuals and diagrams.
4. In `federation_runtime/runtime/core/`, use event-driven navigation through the interactive runtime layer / event bus, while treating `state_store.js` as the stateful store that tracks navigation state.
