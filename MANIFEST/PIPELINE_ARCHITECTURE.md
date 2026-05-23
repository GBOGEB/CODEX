# PIPELINE ARCHITECTURE

## ABACUS_RENDER_PIPELINE

### Canonical Lifecycle

```text
MASTER INPUTS
    ↓
EXTRACTION
    ↓
SSOT NORMALIZATION
    ↓
VALIDATION
    ↓
RENDERING
    ↓
PUBLICATION
    ↓
LINEAGE PERSISTENCE
```

---

## Pipeline Stages

### Extract

Responsibilities:

- PPTX extraction
- OCR extraction
- figure extraction
- speaker-note extraction
- table extraction
- equation extraction

---

### Normalize

Responsibilities:

- SSOT YAML generation
- metadata normalization
- figure normalization
- semantic-card normalization
- unit normalization

---

### Validate

Responsibilities:

- renderer governance checks
- contrast validation
- spacing validation
- thermodynamic validation
- registry validation
- lineage validation

---

### Render

Responsibilities:

- HTML rendering
- PDF rendering
- PPTX rendering
- snapshot rendering
- Plotly rendering
- executive-summary rendering

---

### Publish

Responsibilities:

- GitHub Pages publication
- artifact packaging
- review artifact generation
- regression baseline persistence

---

### Lineage

Responsibilities:

- manifest persistence
- changelog updates
- slide lineage
- figure lineage
- tuple offload updates
- review traceability

---

## Governance Principle

The pipeline must become:

```text
reproducible and deterministic
```

not:

```text
manually orchestrated scripts
```

---

## Future Direction

Future orchestration should include:

- dependency-aware execution
- incremental rebuilds
- artifact caching
- renderer diffing
- backend thermodynamic validation
- publication-grade review packaging
