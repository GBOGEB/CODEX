# CHANGELOG — QPS Master Slide System

## v0.7.0

### Changed

- Chapter 15 content replaced by a generated deck (`gistau-ch15-validated-model`, 9 slides): validated-model overview, helium-4 physics authority (ABACUS pin, HEPAK/CoolProp routing), L1 worked-example results, T05 open item, NIST TN 1334 reference, ideal-gas cross-check domain, engineering toolbox, CI gates, next steps.
- Every figure is generated from committed sources by `tools/build_gistau_deck_content.py`; a test fails when the deck is stale.
- New CSS contract with the SCK CEN 2020 palette (light and dark viewing).

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

## v0.6.1 - Graph navigation MVP + schema hardening

- Added slide/node/review YAML schema drafts under `yaml/`.
- Added eight-node SVG semantic graph MVP with clickable node routing.
- Added HTML graph landing page and per-node detail pages.
- Added side-by-side lineage review prototype (`html/review.html` + YAML review record).
- Added density mode tokens for ultra-dense, engineering-dense, review, and presentation render profiles.

## v0.7.0 - YAML/CSS deck orchestration functional blocks

### Added

- Added `slides.deck_orchestrator` for governed YAML content loading, CSS-based HTML rendering, Markdown handoff generation, and ABACUS manifest emission.
- Added the MINERVA QPS Procurement / AD_07 cybersecurity appendix sample deck source and corporate CSS template.
- Added generated HTML, Markdown, and manifest review artifacts for the first fixed-and-locked target deck.
- Added tests covering normalization, artifact emission, and ABACUS governance controls.
