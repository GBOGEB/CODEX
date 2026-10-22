# CHANGELOG — QPS Master Slide System

## v0.8.0 - Generated semantic navigation graph (v1.3 follow-up #1)

### Changed

- The navigation graph (`svg/navigation/qps-graph-mvp.svg`), its page (`html/graph/index.html`) and the node pages (`html/node/*.html`) are now generated from `yaml/nodes/*.yaml` by `tools/build_qps_node_graph.py`. They are no longer hand-drawn.
- The graph draws both halves of "Tree vs Links": `parent` edges are solid and `interfaces` are dashed, with one lane per link. The hand-drawn MVP drew only the tree.
- Boxes carry the full node id (`QPLANT.WCS`, not `WCS`). Node pages list the record's type, parent, children, interfaces (declared and received), plots, slides, source refs and optional `links`.
- Colors and fonts come from `styles/tokens.yaml`.

### Added

- Fail-closed record validation against `yaml/schema.node.yaml`: missing keys, non-list fields, duplicate ids, unknown parent or interface, self-interface and parent cycles all stop the build.
- `tests/test_qps_node_graph.py` fails when the committed outputs are stale or a link does not resolve. Regenerate with `python tools/build_qps_node_graph.py` (`--check` to verify).

### Not changed

- `data/svg/qps-graph-mvp.svg` stays as it is. It is a fixture copy of the old MVP and an input to the P&ID line and arrow models (`data/model/*.json`), not part of the slide system.

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
