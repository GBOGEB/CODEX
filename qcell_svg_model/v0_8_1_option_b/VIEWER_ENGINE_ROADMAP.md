# Viewer Engine Roadmap - Option B

## Objective

Create a YAML-driven SVG/HTML viewer engine capable of rendering multiple semantic display modes from the same QCELL source model.

## Architecture direction

Draw.io SVG -> extraction layer -> YAML SSOT -> render engine -> SVG/HTML viewer modes

## Proposed engine stages

### Stage 1 - Static extraction

Goal:
- extract geometry;
- labels;
- flows;
- colors;
- grouping metadata.

Output:
- normalized YAML.

### Stage 2 - Layer classification

Goal:
- assign objects into semantic layers.

Initial semantic layers:
- base_thermal_shell
- critical_labels
- teaching_flows
- endpoint_guides
- pressure_diagnostics
- explanatory_annotations

### Stage 3 - Toggle engine

Goal:
- runtime enable/disable layer visibility.

Viewer presets:
- operator
- teaching
- diagnostic

### Stage 4 - Collision engine

Goal:
- dynamic label bumping;
- overlap reduction;
- zoom-aware annotation scaling.

### Stage 5 - Flow simplification engine

Goal:
- replace dense routing with sparse directional hints.

Key rules:
- short local arrows;
- minimal crossings;
- preserve causality clarity;
- reduce visual fatigue.

### Stage 6 - Semantic rendering

Goal:
- adaptive rendering depending on mode.

Examples:
- operator mode suppresses explanatory density;
- teaching mode expands annotation context;
- diagnostic mode enables pressure overlays.

### Stage 7 - GitHub Pages deployment

Goal:
- static hosted viewer.

Potential outputs:
- SVG-only viewer;
- HTML+JS interactive viewer;
- animation-capable review viewer.

## Long-term direction

The final system should behave more like:
- a semantic engineering viewer;
than:
- a static exported drawing.

## Important non-regression rules

- preserve thermal hierarchy dominance;
- keep flows visually subordinate;
- preserve layer independence;
- maintain readability at full-page scale;
- avoid annotation saturation.

## SVG XML source-of-truth correction

The extraction path must now treat the SVG/XML document itself as the primary engineering record. If a source SVG contains Inkscape layers, labels, object IDs, text nodes, colour metadata, or nested group hierarchy, those XML semantics must be preserved before any viewer, YAML/JSON, HTML, or downstream review artifact is produced.

Hard constraints for all future stages:

- do not use OCR;
- do not rasterize the drawing as an extraction input;
- do not parse PDF before SVG/XML;
- preserve Inkscape `inkscape:groupmode="layer"` and `inkscape:label` metadata;
- preserve Draw.io `mxCell` IDs, values, styles, geometry, source/target edges, and parent hierarchy when the lineage artifact is a `.drawio.svg` XML file;
- keep text nodes, labels, object IDs, colour metadata, and group hierarchy available in the generated semantic manifest.

New implementation anchor:

- `qcell_svg_model/tools/svg_xml_extractor.py` extracts SVG/XML semantics directly and records an explicit extraction policy showing OCR, rasterization, and PDF-first parsing are disabled.
- `qcell_svg_model/v0_8_1_option_b/svg_xml_manifest.json` is the regenerated JSON manifest for the current QCELL Draw.io XML lineage source.
