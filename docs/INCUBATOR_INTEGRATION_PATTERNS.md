# INCUBATOR/CODEX/ABACUS Integration Patterns

## Overview

This document describes proven integration patterns between INCUBATOR, CODEX, and ABACUS programs for better pipeline utility, governance alignment, and portable runtime artifacts.

## Integration Architecture

```
┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│  INCUBATOR   │◄───────►│    CODEX     │◄───────►│    ABACUS    │
│  (W000-W003) │         │  (Main Repo) │         │  (Runtime)   │
└──────────────┘         └──────────────┘         └──────────────┘
      │                         │                         │
      │ Tuple Ingress          │ Governance              │ Export
      │ Schema/Naming          │ CI/Pipeline             │ Portability
      │ Category/Theme         │ Semantic Substrate      │ DMAIC Mapping
      └─────────────────────────┴─────────────────────────┘
                    Shared YAML-Driven Governance
```

## Shared Patterns

### 1. YAML-Driven Governance

**Pattern**: Configuration-as-code with schema enforcement

**INCUBATOR Implementation**:
- `incubator/session_tuple_schema.yml` — Schema contract
- `maps/category_map.yml`, `maps/theme_map.yml` — Normalization
- `governance/interfaces/incubator-governance-interface-manifest.yaml`

**ABACUS Implementation**:
- `abacus_runtime/runtime_manifest.yaml`
- `governance/interfaces/abacus-governance-interface-manifest.yaml`

**CODEX Infrastructure**:
- `semantic_substrate/invariants.yaml` (INV-011)
- `scripts/check_manifest.py`, `scripts/check_globs.py`

### 2. Wave Progression Tracking

**Pattern**: Incremental delivery with measurable completion

**Shared Manifest**: `MANIFEST/WAVE_PROGRESSION.yaml`

**INCUBATOR Waves**:
```yaml
incubator_waves:
  - wave: W000 (100%) — Schema & naming
  - wave: W001 (100%) — Local tooling & CI
  - wave: W002 (0%)   — DMAIC mapping
  - wave: W003 (0%)   — Visualization
```

**ABACUS Waves**:
```yaml
waves:
  - wave: A1-A5 (100%) — Foundation
  - wave: A6 (86%)     — Governance runtime
  - wave: A7-A9 (41-67%) — Orchestration & convergence
```

**Integration**: Cross-reference wave identifiers in scripts, dashboards, and documentation.

### 3. Export/Import Portability

**Pattern**: Self-contained runtime bundles for cross-repo use

**Export Scripts**:
- `scripts/export_abacus_runtime.py` — ABACUS bundle
- `scripts/export_incubator_runtime.py` — INCUBATOR bundle

**Structure**:
```
outputs/
├── runtime_export/        # ABACUS
│   └── abacus_runtime/
└── incubator_export/      # INCUBATOR
    ├── incubator/
    ├── maps/
    ├── scripts/
    ├── docs/
    └── EXPORT_METADATA.txt
```

**Bridge**: Export scripts follow identical pattern for consistency.

### 4. CI/Pipeline Validation

**Pattern**: Automated governance checks in GitHub Actions

**Shared CI Steps** (`.github/workflows/ci.yml`):
```yaml
- pytest -q                          # All programs
- python scripts/check_manifest.py   # CODEX
- python scripts/check_globs.py      # CODEX
- python scripts/check_stale.py      # CODEX
- python scripts/check_links.py      # CODEX
- python scripts/validate_tuple.py   # INCUBATOR
- python scripts/export_incubator_runtime.py  # INCUBATOR
```

**Benefit**: Unified validation chain prevents governance drift.

## CODEX/ABACUS Similarities

### Governance Alignment

| Aspect | CODEX | ABACUS | Integration |
|--------|-------|--------|-------------|
| YAML Manifests | ✅ MANIFEST.json, invariants.yaml | ✅ runtime_manifest.yaml | Synchronized semantics |
| Export Scripts | ✅ export_incubator_runtime.py | ✅ export_abacus_runtime.py | Identical pattern |
| Wave Tracking | ✅ WAVE_PROGRESSION.yaml | ✅ Integrated (A1-A9) | Shared manifest |
| CI Validation | ✅ Comprehensive | ✅ Runtime validation | Pipeline integration |
| Semantic Substrate | ✅ Full governance | ✅ Runtime modules | Cross-repo alignment |

### Sync Manifests

**ABACUS ↔ CODEX**: `governance/synchronization/abacus-codex-recursive-sync.yaml`
```yaml
synchronization_domains:
  - governance_semantics
  - runtime_semantics
  - deployment_semantics
  - provenance_semantics
```

**INCUBATOR ↔ CODEX**: `governance/synchronization/incubator-codex-sync.yaml`
```yaml
synchronization_domains:
  - tuple_governance_semantics
  - category_theme_normalization
  - wave_progression_tracking
  - ci_pipeline_integration
  - export_runtime_portability
```

## Category/Theme ↔ DMAIC Mapping

### INCUBATOR Category Alignment

| INCUBATOR Category | ABACUS Domain | Purpose |
|-------------------|---------------|---------|
| INCUBATOR | Prototype | Early-wave scaffolding |
| RUNTIME_GOVERNANCE | Execution | Tuple ingestion control |
| SCHEMA_VALIDATION | Controls | Contract enforcement |

### INCUBATOR Theme → DMAIC Phases

| INCUBATOR Theme | DMAIC Phase | Usage |
|----------------|-------------|-------|
| RUNTIME_GOVERNANCE | Define | Problem scoping |
| SCHEMA_VALIDATION | Measure | Metrics collection |
| THEME_EXTRACTION | Analyze | Pattern discovery |
| INDEX_GENERATION | Improve | Process automation |
| EXPORT_PORTABILITY | Control | Standard enforcement |

**Implementation**: Add `dmaic_phase` field to tuple YAML:
```yaml
dmaic_phase: "define"  # or measure, analyze, improve, control
```

## Pipeline Integration Steps

### Step 1: Consistent Naming

✅ **Completed**:
- All schema/documentation aligned to `W###` pattern
- Tests updated to match convention

### Step 2: Validation Tooling

✅ **Completed**:
- `scripts/validate_tuple.py` — Comprehensive validation
- `tests/incubator/test_validate_tuple.py` — 11 tests
- CI integration in `.github/workflows/ci.yml`

### Step 3: Governance Registration

✅ **Completed**:
- `governance/interfaces/incubator-governance-interface-manifest.yaml`
- `governance/synchronization/incubator-codex-sync.yaml`
- `semantic_substrate/invariants.yaml` — INV-011 enhanced

### Step 4: Export Validation

✅ **Completed**:
- CI validates export bundle generation
- Metadata includes bridge references
- Test coverage in `tests/incubator/test_export_incubator_runtime.py`

### Step 5: W002 DMAIC Integration (Planned)

🔜 **Next Wave**:
- Add DMAIC phase validation to `scripts/validate_tuple.py`
- Create DMAIC → ABACUS orchestration mapping
- Add category/theme mapping validation scripts
- Update `maps/category_map.yml` with ABACUS domain references

### Step 6: W003 Visualization (Planned)

🔜 **Future**:
- Plotly timeline dashboard (similar to `visuals/wave_progress.py`)
- Theme heatmaps showing tuple distribution
- Tuple analytics integrated into `dashboards/`

## Dormant Code Analysis

**Status**: No dormant or deprecated INCUBATOR code found.

All INCUBATOR artifacts follow the "active" status convention established in the main repository. The tuple schema explicitly defines status values:
```yaml
allowed_status:
  - active
  - archived
  - draft
```

## Utility Improvements

### For Developers

1. **Validation Hook**: Run `scripts/validate_tuple.py` before committing tuples
2. **Export Bundle**: Use `scripts/export_incubator_runtime.py` for portable sharing
3. **Index Generation**: Auto-generate docs with `scripts/build_incubator_index.py`

### For CI/CD

1. **Pipeline Validation**: Tuple validation integrated into CI workflow
2. **Export Testing**: CI validates export bundle generation
3. **Semantic Enforcement**: INV-011 enforced via semantic substrate

### For Cross-Repo Portability

1. **INCUBATOR → ABACUS**: Use export bundle + DMAIC mapping (W002)
2. **ABACUS → INCUBATOR**: Reverse-map orchestration domains to categories
3. **Shared Governance**: Both reference `WAVE_PROGRESSION.yaml`

## Implementation Checklist

- [x] Fix naming convention inconsistencies
- [x] Add robust validation utility (`validate_tuple.py`)
- [x] Create governance interface manifests
- [x] Create synchronization manifests
- [x] Enhance semantic substrate (INV-011)
- [x] Integrate validation into CI
- [x] Add comprehensive test coverage (24 tests)
- [ ] Implement DMAIC phase validation (W002)
- [ ] Create category/theme validation scripts (W002)
- [ ] Add tuple analytics dashboards (W003)

## References

- `docs/INCUBATOR_ABACUS_BRIDGE.md` — Original bridge documentation
- `docs/incubator_runtime_map.md` — Runtime documentation
- `MANIFEST/WAVE_PROGRESSION.yaml` — Wave tracking
- `governance/interfaces/` — Governance interface manifests
- `governance/synchronization/` — Sync manifests

## Contact & Lineage

- **Program**: INCUBATOR
- **Repository**: CODEX
- **Owner**: @GBOGEB
- **Integration**: W001 (Complete), W002 (Planned)
