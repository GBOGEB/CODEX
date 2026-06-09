# DMAIC Reconciliation Review

## Scope

| Category | Path |
|---|---|
| New PR-000 artifact | `docs/DMAIC/` |
| Existing DMAIC process | `99_handover/PROCESS_DMAIC.md` |
| Existing DMAIC phase map | `maps/dmaic_phase_map.yml` |

## Finding

PR-000 creates a generic DMAIC template that overlaps with the existing recursive build and DMAIC control plan. The existing process already defines all five DMAIC phases and anchors them to concrete engineering metrics, artifacts, workflow steps, and control mechanisms.

## Overlap Assessment

| Dimension | Evidence | Assessment |
|---|---|---|
| Phase model | Both use Define, Measure, Analyze, Improve, Control. | Complete lifecycle overlap. |
| Metrics | Existing process includes leakage, helium loss, PSV completeness, and tag conformance. | New template lacks domain metrics. |
| Artifacts | Existing process names MASTER_DIFF, MASTER_PATCH, RTM, ITP, QA, P&ID, BOM, ADR, OCD, vendor summary, and `.glob`. | New template only links RTM/ADR. |
| Workflow | Existing process defines generation, parsing, artifact production, ranking, patching, and transfer. | New template has no workflow. |
| Control | Existing process defines QA review, alerts, SEED tag, and archive behavior. | New template leaves Control blank. |

## Metrics

- `dmaic_overlap_pct`: **74**
- Lexical new-term coverage against existing DMAIC corpus: **39.6%**
- Template compatibility: **medium-high**, because the phase names align but the new template omits existing domain-specific measurement and control fields.

## Template Compatibility

The new `docs/DMAIC/template.md` can be retained only if it adds compatibility fields for:

- Target metric / baseline.
- Measurement method.
- Root-cause hypothesis.
- Improvement artifact.
- Control owner.
- Existing workflow step.
- Related RTM / ADR / handover artifact.

## Consolidation Opportunities

1. Use `99_handover/PROCESS_DMAIC.md` as the canonical DMAIC process baseline.
2. Convert `docs/DMAIC/README.md` into a portal/index for the process baseline.
3. Convert `docs/DMAIC/template.md` into a lightweight intake form that explicitly references `99_handover/PROCESS_DMAIC.md`.
4. Register DMAIC phase mapping compatibility with `maps/dmaic_phase_map.yml` before expanding templates.

## Recommendation

Classify `docs/DMAIC/` as **BRIDGE**. It should bridge to the existing DMAIC process and phase map rather than create a separate DMAIC system.
