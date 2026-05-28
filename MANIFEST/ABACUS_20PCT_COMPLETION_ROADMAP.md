# ABACUS +20% Completion Roadmap

**Generated:** 2026-05-28  
**Baseline:** `completion_estimate_percent = 64` | `overall_convergence_score = 71`  
**Target:** `completion_estimate_percent ≥ 84` | `overall_convergence_score ≥ 88`  
**Strategy:** Activate dormant layers first; raise stalled waves second.

> **Metric definitions:**  
> `completion_estimate_percent` — weighted average of all program dimension scores in  
> `MANIFEST/PROGRAM_METRICS.yaml` (governance, renderer, CI/CD, orchestration, visualization,  
> thermodynamics, validation, publication readiness).  
> `overall_convergence_score` — ABACUS quality gate composite in `MANIFEST/CONVERGENCE_KPIS.yaml`  
> calculated as the weighted mean of governance, orchestration, telemetry, renderer quality,  
> publication readiness, thermodynamic validity, backend convergence, and scientific confidence  
> scores. Both metrics are on a 0–100 scale.

---

## Current State Diagnosis

The ABACUS render pipeline has **arrested development** concentrated in three bands:

| Band | Layers | Score | Condition |
|------|--------|-------|-----------|
| **Dormant incubator** | W002 (DMAIC phase mapping), W003 (visualization) | 0% / 0% | Never started |
| **Dormant physics** | `backend_convergence_score`, `scientific_confidence_score` | 18 / 31 | Scaffolded but blocked |
| **Stalled waves** | A7 (orchestration telemetry), A9 (scientific convergence) | 41% / 52% | Partially started, no momentum |

These gaps represent most of the distance to 84%.  
Waves A1–A5 are complete (100%). A6 is at 86%.

---

## Target Delta by Dimension

| Dimension | Baseline | Target | Delta |
|-----------|----------|--------|-------|
| `backend_convergence_score` | 18 | 38 | +20 |
| `thermodynamic_validity_score` | 38 | 52 | +14 |
| `scientific_confidence_score` | 31 | 48 | +17 |
| `publication_readiness_score` | 64 | 78 | +14 |
| `ci_cd` (program metrics) | 62 | 78 | +16 |
| W002 wave completion | 0% | 60% | +60pp |
| W003 wave completion | 0% | 40% | +40pp |
| A7 wave completion | 41% | 65% | +24pp |
| A9 wave completion | 52% | 72% | +20pp |
| A6 wave completion | 86% | 100% | +14pp |

---

## Phase 1 — Activate Dormant Incubator Waves (W002, W003)

**W002: DMAIC Phase Mapping**  
Currently blocked because `maps/category_map.yml` has only one category (`INCUBATOR`)
and `maps/theme_map.yml` has only one theme (`RUNTIME_GOVERNANCE`).
No DMAIC-phase-to-category bridge exists.

Tasks:
1. Expand `maps/category_map.yml` with DMAIC-aligned categories:
   `DELIVERY`, `GOVERNANCE`, `ANALYSIS`, `IMPROVEMENT`, `CONTROL`
2. Expand `maps/theme_map.yml` with domain themes:
   `SCIENTIFIC_VALIDATION`, `BACKEND_CONVERGENCE`, `DEFINE`, `MEASURE`, `ANALYZE`,
   `IMPROVE`, `CONTROL`
3. Create `maps/dmaic_phase_map.yml` — INCUBATOR category → DMAIC phase bridge metadata.
4. Add a W002 validator script `scripts/validate_dmaic_phase_map.py` that checks
   every session tuple in `incubator/` has a valid DMAIC phase assignment.
5. Emit completeness metric to `MANIFEST/WAVE_PROGRESSION.yaml`.

**Done criterion:** All existing incubator tuples resolve to a DMAIC phase without error.  
**Estimated W002 completion after:** 60%

---

**W003: Visualization and Dashboards**  
Blocked by W002 not providing structured data.

Tasks:
1. After W002 ships: create `visuals/incubator_dmaic_dashboard.py` (Plotly timeline
   grouped by DMAIC phase, coloured by category, following patterns in
   `visuals/wave_progress.py`).
2. Add `docs/incubator-dmaic-dashboard.html` entry point.
3. Register new HTML in `MANIFEST.json` `published_pages`.
4. Wire into CI via existing check scripts.

**Done criterion:** Dashboard renders and passes CI link/stale checks.  
**Estimated W003 completion after:** 40%

---

## Phase 2 — Complete Wave A6 (86% → 100%)

Four linting scripts are listed in the existing `MANIFEST/ROADMAP.md` as pending.
These are the only open A6 items.

Tasks:
1. `governance/contrast_lint.py` — enforce WCAG contrast ratios from
   `governance/SEMANTIC_THEME.yaml` (already checked by `WCAG_CONTRAST_CHECKER.py`;
   this lint surface is a CI hook wrapper).
2. `governance/overflow_lint.py` — detect horizontal overflow in rendered HTML.
3. `governance/spacing_lint.py` — validate CSS spacing tokens match theme contract.
4. `governance/navigation_lint.py` — validate `docs/index.html` link graph stays
   within `docs/` (mirrors existing `check_links.py` logic).

**Done criterion:** All four lint scripts importable, each returns exit code 0 on
the current `docs/` tree.

---

## Phase 3 — Unblock Wave A7 (41% → 65%)

A7 focus: `orchestration_dependency_and_visual_telemetry`

Root cause of stall: no live orchestration dependency graph is being emitted;
`visuals/` dashboards do not consume `agent_runtime/agent_topology.json`.

Tasks:
1. Add `visuals/orchestration_dependency_graph.py` — reads
   `agent_runtime/agent_topology.json`, emits Plotly network graph HTML.
2. Add `visuals/agent_telemetry_timeline.py` — reads
   `agent_runtime/agent_metrics.json`, emits timeline of agent completions.
3. Register both outputs in `MANIFEST.json`.
4. Wire export into `scripts/export_abacus_runtime.py`.

**Done criterion:** Both HTML outputs generated in CI and published to Pages.

---

## Phase 4 — Advance Wave A9 (52% → 72%)

A9 focus: `scientific_convergence_and_thermo_command_center`

Root cause of stall: `backend_convergence_score = 18`, `REFPROP = 12`, `HEPAK = 9`.
The thermo command center cannot converge without backend scaffolding.

Tasks:
1. Create `physics/backend_registry.yaml` — declares available backends
   (CoolProp, REFPROP, HEPAK, NIST) with availability flags and version pins.
2. Create `physics/backend_adapter.py` — thin adapter interface; each backend
   implements a `get_saturation_properties(T)` method; missing backends raise a
   governed `BackendUnavailable` exception rather than crashing.
3. Add `tests/test_backend_adapter.py` — mock-based tests for the adapter
   contract; does not require actual HEPAK/REFPROP licenses.
4. Update `dashboards/thermo_command_center.py` to consume `backend_registry.yaml`
   rather than hard-coding backend names.

**Done criterion:** `backend_adapter.py` importable, tests pass, `backend_convergence_score`
advances to ≥ 35 (logged in `MANIFEST/THERMODYNAMIC_KPIS.yaml`).

---

## Phase 5 — Improve CI/CD Score (62 → 78)

Tasks:
1. Add render-regression test stub in `.github/workflows/ci.yml`:
   run `visuals/*.py` in headless mode and assert outputs are non-empty.
2. Ensure `check_stale.py` covers all HTML files added by W003 and A7 phases above.
3. Add `scripts/check_backend_registry.py` — validates `physics/backend_registry.yaml`
   schema and that all declared-available backends are importable.

---

## Completion Accounting

| Phase | Waves touched | Dimension gains | Contribution to +20% |
|-------|---------------|-----------------|----------------------|
| 1 (W002 + W003) | W002: 0→60%, W003: 0→40% | publication_readiness +8 | ~4% |
| 2 (A6) | A6: 86→100% | governance +6, ci_cd +4 | ~3% |
| 3 (A7) | A7: 41→65% | orchestration +8, visualization +5 | ~5% |
| 4 (A9) | A9: 52→72% | backend_convergence +17, thermodynamic +8 | ~5% |
| 5 (CI/CD) | cross-cutting | ci_cd +12 | ~3% |
| **Total** | | | **~20%** |

---

## Sequencing Constraints

```
W002 ──must precede──→ W003
W002 ──must precede──→ A7 (telemetry feeds incubator)
Phase 2 (A6 lint)  ──independent──
Phase 4 (A9 physics) ──independent──
Phase 5 (CI/CD)    ──must follow──→ Phase 1 + 3 (covers new HTML outputs)
```

---

## Non-Goals (out of scope for this +20% window)

- Git LFS, S3, Kubernetes (deferred to W003+, per existing `MANIFEST/ROADMAP.md`)
- Full HEPAK/REFPROP license integration (backend_adapter scaffolds the interface only)
- Phase 1C–1E CRYO_LINAC recursive execution
- He-II saturation dome (H7 in existing roadmap — deferred)
- `release_candidate` gate (score 34, needs scientific validation beyond this window)
