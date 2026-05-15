# QPS Master Slide System

HTML-first dense engineering knowledge-transfer system for QPS slide decks.

## Version

`v0.5.0` — HTML render + YAML seed pass.

## Purpose

This package captures the current QPS slide-system direction developed from the uploaded candidate decks:

- `STYLE_SYSTEM` — visual grammar, palette, overlays, navigation, review blocks.
- `SBS_NAMING` — QSYS/QPS hierarchy, SBS, terminal points, tag grammar, Ultimo-style ontology mapping.
- `CONTROL_SYSTEM` — QPS:CIS hierarchy, MIT/MIS/MCS signal philosophy, WCS.HCC inheritance, inhibition logic.
- `UTILITIES_SYSTEM` — HVAC, PCW, RCW, ES02, LOOP, HCC heat-flow and operational assumptions.

## Design Principle

The goal is not low-density presentation design. The goal is dense, coherent, topic-specific master slides with controlled semantic navigation.

```text
YAML source -> HTML render -> PDF/PPTX review artefacts
```

## Current repository files

- `README.md` — package overview, scope, and implementation direction.
- `CHANGELOG.md` — versioned progress log.

## Planned/generated artefacts

- `index.html` — planned HTML preview and navigation entry.
- `index.yaml` — planned system/deck index draft.
- `schema.slide.yaml` — planned slide source schema draft.

## Review status

This is a first GitHub/Codex-ready scaffold. It intentionally keeps the render lightweight while preserving the architecture, terminology, and deck split for the next implementation pass.


## v0.5 Delivery

- Added runnable `index.html` with HTML-native navigation.
- Added `index.yaml` system index.
- Added first deck YAML files with two master slides each.
- Added style token file and duplicate/reference map.
