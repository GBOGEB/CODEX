# CHANGELOG — QPS Master Slide System

## v0.4.0

### Added

- Initial documentation for the QPS master-slide system structure and direction.
- Proposed HTML-first navigation/index architecture.
- Proposed initial deck split:
  - STYLE_SYSTEM
  - SBS_NAMING
  - CONTROL_SYSTEM
  - UTILITIES_SYSTEM
- First-pass documentation of master-slide candidates.
- Draft definition of the recursive/idempotent/evolutionary DMAIC model.
- Draft notes for KPI tracking, phase maturity metrics, and a YAML source model.

### Key Findings

- Dense engineering master slides should remain high-density.
- Duplicates should become references/interludes rather than repeated slides.
- Tree vs Links is a core architectural concept for QPS.
- Styles are semantic visual dialects, not isolated themes.

### Next Actions

- Add canonical slide inventory.
- Add schema.slide.yaml.
- Add index.yaml.
- Add rendered HTML master-slide examples.
- Add reference/interlude linking system.

## v0.5.0

### Added

- Rendered `index.html` with HTML-native section anchors and navigation links.
- Initial YAML index and deck files for STYLE_SYSTEM and CONTROL_SYSTEM.
- Second master slide per deck to validate slide sequence behavior.
- Reference/interlude linking between decks.
- Duplicate/reference canonical map file.
- Style token source file for color/spacing/typography/emphasis.


## v0.6.0

### Added

- Chapter 15 calculator tool scaffold in `src/ch15_calculator_tool.py`.
- Version metadata loading from `VERSION.json` for reproducible calculation lineage.
- Unit tests for total-with-contingency, failure-rate, and version loading behavior.

### Purpose

- Start Chapter 15 implementation as a calculator-focused workstream with explicit versioning semantics.

- Sample input JSON added at `inputs/ch15/sample_input_v1.json` and deterministic stats builder added for governance-ready outputs.
