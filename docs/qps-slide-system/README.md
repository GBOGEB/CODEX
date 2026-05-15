# QPS Master Slide System

HTML-first dense engineering knowledge-transfer system for QPS slide decks.

## Version

`v0.4.0` — indexed master-output pass.

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

## Current artefacts

- `index.html` — first HTML preview and navigation entry.
- `index.yaml` — system/deck index draft.
- `schema.slide.yaml` — draft slide source schema.
- `CHANGELOG.md` — versioned progress log.

## Review status

This is a first GitHub/Codex-ready scaffold. It intentionally keeps the render lightweight while preserving the architecture, terminology, and deck split for the next implementation pass.
