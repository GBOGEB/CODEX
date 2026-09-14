# NEXT EXECUTION — v1.6

## Mission

Promote the visual knowledge system from graph-binding MVP to source-bound dense engineering decks.

## v1.6 Definition of Done

### A. Actual source binding
For every promoted canonical slide:

```yaml
source:
  deck_id:
  deck_filename:
  slide_number:
  source_image:
  source_format:

extraction:
  text:
  tables:
  diagrams:
  notes:

visual_dna:
  style_family:
  layout:
  density:
  palette:
  typography:

curated:
  deck:
  slide_id:
  node_ids:

change:
  classification:
  rationale:
  review_status:
```

Do not infer missing source identifiers.

### B. Utilities dense canonical deck
Minimum topics:
1. title / navigation / progress
2. utility context
3. HCC cooling loads
4. HCC thermal topology — HX1/HX2/HX3/HX4/Q5
5. HVAC / PCW / RCW interaction
6. LOOP operational chain
7. ODH / occupancy implications
8. plots
9. validation / assumption register
10. interfaces / responsibilities
11. source lineage

Canonical utility anchors currently in scope:
- PAB12 — PCW / primary cooling interface
- HV06 — RCW / HCC oil HX2 / heat recovery
- HV03 — WCS room HVAC / ventilation / occupancy context
- ES02 — electrical backup / LOOP envelope

### C. Controls dense canonical deck
Minimum topics:
1. title / navigation / progress
2. QPS:CIS architecture
3. SBS / control hierarchy
4. MIT / MIS / MCS signal philosophy
5. WCS.HCC HP1..HP4 control decomposition
6. WCS I/O candidate matrix
7. QINFRA I/O candidate matrix
8. readiness / inhibition
9. interfaces
10. L1/L2/FAT/SAT progression
11. source lineage

Do not duplicate the full LOOP engineering inside Controls. Controls should reference the Utilities-owned scenario and carry only mode/signal/inhibit consequences.

### D. Graph UX completion
- node hover summary
- parent / child navigation
- breadcrumb traversal
- relevant deck / plot / table links
- source lineage entry point
- side inspector or equivalent in-page interaction

### E. YAML-first generation
Move toward:

```text
nodes.yaml + edges.yaml + bindings.yaml
        ↓
render/generator
        ├── calculate levels / positions
        ├── route tree edges
        ├── route interface links
        ├── create anchors
        ├── create node pages
        └── create indexes
        ↓
graph.svg + graph.html + node pages
```

Semantic YAML is SSOT; geometry is render metadata.

## Version progression

```text
v1.4  CLICKABLE GRAPH MVP                    DONE
  ↓
v1.5  GRAPH BINDING + LINEAGE CONTRACT       MVP DONE / PARTIAL TARGET
  ↓
v1.6  REAL SOURCE + DENSE UTIL/CTRL          NEXT
  ↓
v1.7  TRUE YAML → SVG/HTML GENERATOR
  ↓
v1.8  HTML → PDF/PPTX/ODP PIPELINE
  ↓
v1.9  STATIC HOST + ADVANCED REVIEW UX
  ↓
v2.0  CONTROLLED STATIC KNOWLEDGE SYSTEM
```

## Suggested follow-up PR title

`SOURCE+DECKS: bind original slide lineage and promote dense Utilities/Controls`

## Suggested additive path

`docs/qps-source-bound-dense-decks-v1-6/`
