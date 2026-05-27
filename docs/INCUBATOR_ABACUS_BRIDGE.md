# INCUBATOR ↔ ABACUS Bridge Integration

## Purpose

This document defines the integration points between CODEX INCUBATOR (chat/session tuple ingress) and ABACUS (DMAIC orchestration) systems, following the bridge architecture documented in `docs/ALPHA_BRIDGE_ABACUS_CODEX.md`.

## Architecture Alignment

```
INCUBATOR (CODEX)           Bridge Layer              ABACUS Runtime
─────────────────────────────────────────────────────────────────────
Chat tuple ingress    →    Tuple validation    →    DMAIC execution
Session data capture  →    Category mapping    →    Multi-agent orchestration
Theme extraction      →    Phase mapping       →    Convergence metrics
Local indexing        →    Export/import       →    Governance telemetry
```

## Shared Patterns

### 1. YAML-Driven Governance

**INCUBATOR (CODEX):**
- `incubator/session_tuple_schema.yml` — tuple contract
- `maps/category_map.yml` — category governance
- `maps/theme_map.yml` — theme normalization
- `maps/repo_ingress_map.yml` — routing specification

**ABACUS Equivalent:**
- DMAIC phase schemas
- Orchestration category mappings
- Cluster domain definitions
- Runtime module routing

**Bridge Action:** Align INCUBATOR category/theme maps with ABACUS orchestration domains for seamless handoff.

### 2. Wave-Based Progression

**INCUBATOR (CODEX):**
- W000: Schema and naming
- W001: Local ingestion/indexing
- W002: DMAIC phase mapping (planned)
- W003: Visualization (planned)

**ABACUS Equivalent:**
- A1-A9: YAML extraction → convergence telemetry
- Wave progression governance in `MANIFEST/WAVE_PROGRESSION.yaml`

**Bridge Action:** INCUBATOR waves W00X now registered in `MANIFEST/WAVE_PROGRESSION.yaml` alongside ABACUS A1-A9.

### 3. Export/Import Patterns

**INCUBATOR (CODEX):**
- `scripts/export_incubator_runtime.py` — portable export to `outputs/incubator_export/`

**ABACUS Equivalent:**
- `scripts/export_abacus_runtime.py` — portable export to `outputs/runtime_export/`

**Bridge Action:** Both systems use identical export structure for cross-repo portability.

### 4. Markdown/HTML Artifact Generation

**INCUBATOR (CODEX):**
- `scripts/build_incubator_index.py` → `docs/incubator_index.md`
- `docs/incubator_runtime_map.md`

**ABACUS Equivalent:**
- HTML dashboard ecosystem (Plotly/interactive)
- Runtime documentation generation

**Bridge Action:** INCUBATOR W003 will introduce Plotly dashboards following ABACUS patterns.

## Category and Theme Alignment

### INCUBATOR Categories → ABACUS Domains

| INCUBATOR Category | ABACUS Domain | Bridge Mapping |
|-------------------|---------------|----------------|
| INCUBATOR         | prototype     | Early wave scaffolding |
| DELIVERY          | execution     | Implementation tasks |
| GOVERNANCE        | controls      | Policy and gating |

### INCUBATOR Themes → ABACUS DMAIC Phases

| INCUBATOR Theme | ABACUS DMAIC Phase | Mapping Notes |
|----------------|-------------------|---------------|
| RUNTIME_GOVERNANCE | Define | Policy definition and routing |
| CHAT_TUPLE | Measure | Data capture and ingestion |
| STATIC_RENDERING | Analyze | Index generation and theme extraction |
| *Future themes* | Improve, Control | To be mapped in W002 |

## Integration Roadmap

### W000/W001 (Complete)
- ✅ Schema and naming convention
- ✅ Local parser and validation
- ✅ Markdown index generation
- ✅ CI validation integration
- ✅ Test coverage

### W002 (Planned)
- [ ] DMAIC phase validation against maps
- [ ] Category/theme map refinement for ABACUS alignment
- [ ] Bridge metadata schema
- [ ] Tuple handoff protocol to ABACUS orchestration

### W003 (Future)
- [ ] Plotly timeline dashboard (following ABACUS dashboard patterns)
- [ ] Theme heatmap visualization
- [ ] Tuple analytics and trends
- [ ] Integration with `agent_runtime/agent_metrics.json`

## Governance and Validation

### INCUBATOR Governance Files
- `semantic_substrate/invariants.yaml` — INV-011 tuple integrity
- `.github/workflows/ci.yml` — Tuple parsing validation
- `tests/incubator/` — Pytest coverage

### ABACUS Governance Equivalent
- Tuple validation framework
- DOW (Deployment Orchestration Workflow) governance
- KEB (Knowledge Execution Backbone) validation

## Export and Portability

Both systems support portable export:

```bash
# INCUBATOR export
python scripts/export_incubator_runtime.py
# → outputs/incubator_export/

# ABACUS export
python scripts/export_abacus_runtime.py
# → outputs/runtime_export/
```

Export structure includes:
- Source YAML/tuple files
- Mapping/schema files
- Parser/builder scripts
- Generated documentation
- Export metadata

## Future Bridge Activation

When W002 activates ABACUS bridge:

1. **Tuple Handoff**: INCUBATOR tuples export to ABACUS ingress
2. **Category Mapping**: Shared category_map.yml consumed by both systems
3. **DMAIC Integration**: Tuple `dmaic_phase` field validated against ABACUS phases
4. **Telemetry Sharing**: INCUBATOR metrics feed into ABACUS convergence telemetry

## References

- **ABACUS Bridge Architecture**: `docs/ALPHA_BRIDGE_ABACUS_CODEX.md`
- **INCUBATOR Schema**: `incubator/session_tuple_schema.yml`
- **Wave Progression**: `MANIFEST/WAVE_PROGRESSION.yaml`
- **Semantic Invariants**: `semantic_substrate/invariants.yaml`
- **ABACUS Runtime**: `abacus_runtime/runtime_manifest.yaml`

## Principle

> "INCUBATOR (CODEX) provides the ingress substrate. ABACUS provides the orchestration intelligence. The bridge ensures no duplication."

---

**Program**: INCUBATOR
**Repository**: CODEX
**Bridge Status**: Phase 1 (W000/W001) Complete
**Next Milestone**: W002 DMAIC Integration
