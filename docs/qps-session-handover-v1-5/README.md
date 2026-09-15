# QPS Visual Knowledge System — Session Handover v1.5

## Purpose

Freeze the current engineering state at the end of the session and provide an explicit restart contract for the next implementation cycle.

This path is **additive only**. It does not overwrite prior decks, render systems, or historical versions.

## Golden thread

```text
PPTX / PDF / ODP / slide-image ZIP
        ↓
source extraction + visual lineage
        ↓
YAML semantic object layer
        ↓
HTML engineering knowledge surface
        ↓
SVG / Plotly / tables / graph navigation
        ↓
PDF / PPTX / ODP / Markdown / static host
        ↓
review + lineage + recursive iteration
```

Core rule:

> Slides are semantic engineering artefacts, not presentation pages.

HTML is the primary engineering surface. PPTX is an export/review target.

## Current version lineage

| Version | Purpose | State |
|---|---|---|
| v1.0b | implementation architecture + theme/title system | established |
| v1.1 | blue-white SBS + title grammar + asset ontology + SVG plots | prototype |
| v1.2 | visual/navigation test + Plotly/SVG fallback | prototype |
| v1.3 | additive individual-deck/render architecture | merged via PR #59 |
| v1.4 | clickable SVG semantic graph MVP | local MVP |
| v1.5 | graph-to-deck/plot/table binding + lineage contract | local MVP / partial target completion |

Merged architecture milestones:
- PR #56
- PR #59

## v1.5 acceptance state

v1.5 is **not** full source-lineage completion.

It delivered:
- graph → deck bindings
- graph → plot bindings
- graph → table bindings
- YAML node objects
- HTML node pages
- source-lineage registry structure
- source-vs-curated comparison contract
- dense Utilities / Controls / Naming / Asset binding targets

Still open:
1. exact source PPTX/PDF/image slide binding
2. source deck + slide number + source image + extracted text population
3. full canonical dense Utilities deck
4. full canonical dense Controls deck
5. true YAML → SVG/HTML layout generator
6. node hover/side inspector UX
7. deterministic HTML → PDF/PPTX/ODP export pipeline

## Non-negotiable governance

- additive versioning only
- do not silently overwrite previous deck versions
- do not fabricate source slide IDs
- preserve user visual lineage
- preserve dense engineering cognition
- multiple style families are intentional
- promote to canonical only after review

## Style families

- `corporate_purple` — authority / titles / governance
- `engineering_blue_white` — SBS / Controls / I/O / ICD-like dense content
- `sbs_green` — hierarchy / SSOT
- `operational_apricot` — LOOP / degraded modes / assumptions
- `review_yellow_red` — critique / unresolved actions
- `dark_control_room` — live HTML review
- `print_minimal` — PDF/static review

## Next canonical target

**v1.6 = REAL SOURCE BINDING + DENSE UTILITIES / CONTROLS**

See `NEXT_EXECUTION_v1_6.md`.
