# ADDENDUM — Multi-Format Output Triage Logic

Apply this triage model in addition to the current planned `OUTPUT_1_BASELINE` (that is, the baseline output specification / primary single-output plan that this addendum extends).

The leak-rate dashboard is one engineering topic, but it must generate several outputs with different purpose, audience, and density.

## 1) Output Triage Principle

One source topic shall generate multiple coordinated artefacts:

```text
Same engineering truth
Different audience
Different density
Different format
Same traceability
```

The source of truth remains:

```text
Markdown + YAML + JSON data + Python calculation engine
```

Generated outputs:

```text
HTML dashboard
Markdown handover
PDF handover
RTM table
JSON/YAML traceability
GitHub Pages static portal
```

Do not let any generated output become an independent source of truth.

---

## 2) Audience / Density Mapping

| Output                   | Audience                      | Density      | Purpose                             |
|--------------------------|-------------------------------|--------------|-------------------------------------|
| `index.html`             | Technical peer / reviewer     | Medium       | Navigation portal                   |
| `dashboard.html`         | Engineer / decision-maker     | Visual first | Interactive leak-rate dashboard     |
| `calculations.html`      | Cryogenic engineer            | High         | Formula proof and worked examples   |
| `handover.md`            | Coding agent / VS Code / Git  | High         | Source-readable handover            |
| `handover.pdf`           | Formal reviewer / stakeholder | Medium-high  | Controlled issue pack               |
| `rtm_traceability.html`  | QA / requirements reviewer    | High         | RTM and source mapping              |
| `executive_summary.html` | Manager / non-specialist      | Low-medium   | Decision summary and recommendation |
| `developer_notes.md`     | Codex / future maintainer     | High         | Build logic and extension rules     |

---

## 3) Required View Modes

```text
HTML Preview
Code-like Markdown
PDF / Print Mode
Expand All
Collapse All
Export PDF
```

HTML shell requirements:

```text
details / summary sections
sticky navigation
print CSS
badges for ACCEPT / REVIEW / RISK / TRACE
```

Use the provided HTML scaffold as the visual and structural pattern.

---

## 4) Engineering Triage Object Types

Every extracted item must be classified into one of:

```text
Decision
Requirement
Assumption
Risk
Action
Interface
Evidence
Generated Artefact
Calculation
Plot
Validation Check
```

Each item shall carry:

```text
id
title
type
source
status
owner
density_level
audience
trace_reference
version_added
```

---

## 5) Status Badges

```text
ACCEPT = mature enough for baseline
REVIEW = technically plausible but needs checking
RISK = unresolved, unsafe, contradictory, or assumption-heavy
TRACE = source-linked evidence item
TODO = required implementation work
NEXT = next recommended step
DONE = implemented baseline feature
```

---

## 6) Leak Dashboard Specific Triage

```yaml
Visual-first:
  - dashboard plots
  - log-log leak-rate comparison
  - valve-class comparison
  - cost versus leak-tightness plot
  - fleet-size sensitivity
Calculation-first:
  - unit conversion
  - helium mass-loss equation
  - sonic/choked-flow check
  - Reynolds number estimate
  - pressure and temperature sensitivity
  - worked examples
Requirement-first:
  - RTM-047 to RTM-051
  - leak-rate table
  - helium inventory table
  - Slide 15 warm-valve concern
  - EN 13185 leak-detection anchor
Decision-first:
  - where 1e-9 is overkill
  - where 1e-8 is justified
  - where 1e-4 is acceptable only for valve-seat/internal leakage
  - where 1e-3 is rejected boundary case
Reliability-first:
  - MTBF
  - MTTR
  - MDT
  - availability
  - spare strategy
  - critical valve consequence
```

---

## 7) Recursive DMAIC Layer (Total + Subsystems)

Apply this recursive loop to each output view and each subsystem slice (visual, calculations, traceability, reliability):

```text
DEFINE: What is this view for?
MEASURE: What data does it contain?
ANALYZE: What engineering question does it answer?
IMPROVE: How does it improve understanding?
CONTROL: How is it versioned and kept traceable?
```

Each output file shall include a short **DMAIC View Note**.

---

## 8) Idempotency Rule

```text
same inputs
same assumptions
same code version
same templates
=
same generated outputs
```

Generate `OUTPUT_MANIFEST.json` with:

```text
file path
file type
purpose
audience
density
hash
generated timestamp
source inputs
builder version
```

---

## 9) ASCII Architecture / Hierarchy / Repo Broadcast

### 9.1 System architecture (ASCII)

```text
[Markdown/YAML/JSON Sources] ---> [Python Build Engine] ---> [Generated Artefacts]
         |                               |                         |
         v                               v                         v
 [Traceability Anchors]          [Validation + Smoke]      [docs/*.html + pdf + md]
         |                               |                         |
         +----------------------> [OUTPUT_MANIFEST.json] <---------+
```

### 9.2 Build hierarchy (ASCII)

```text
Tier 0: Source of Truth
  - source/*.md
  - data/*.json
  - assumptions/*.yaml
Tier 1: Compute & Transform
  - src/calc_leak_rate.py
  - src/generate_dashboard.py
  - src/build_handover.py
  - src/manifest.py
Tier 2: QA + Smoke + Scout
  - self_smoke (idempotency, schema, hash)
  - functional_smoke (navigation, plots, export)
  - bidirectional_scout (source<->output trace)
Tier 3: Publication
  - docs/*.html
  - docs/handover.pdf
  - GitHub Pages static hosting
```

### 9.3 GitHub Pages broadcast model

```text
git push -> GitHub Actions (optional) -> docs/ as static site -> Pages URL

Navigation:
  index.html
    ├─ dashboard.html
    ├─ calculations.html
    ├─ rtm_traceability.html
    ├─ executive_summary.html
    └─ handover.html / handover.pdf
```

Javascript behavior expected in `assets/triage.js`:
- clickable section navigation
- expand/collapse all blocks
- refresh/reload view state
- print/export-friendly handling

---

## 10) Release Structure

```text
leak_rate_helium_dashboard/
├─ docs/
│  ├─ index.html
│  ├─ dashboard.html
│  ├─ calculations.html
│  ├─ executive_summary.html
│  ├─ rtm_traceability.html
│  ├─ handover.html
│  └─ handover.pdf
├─ source/
│  ├─ handover.md
│  ├─ assumptions.md
│  ├─ developer_notes.md
│  └─ rtm_traceability.md
├─ data/
│  ├─ leak_classes.json
│  ├─ valve_candidates.json
│  ├─ scenarios.json
│  └─ source_anchors.json
├─ src/
│  ├─ calc_leak_rate.py
│  ├─ generate_dashboard.py
│  ├─ build_handover.py
│  └─ manifest.py
├─ assets/
│  ├─ style.css
│  └─ triage.js
├─ outputs/
│  ├─ plots/
│  ├─ tables/
│  └─ manifests/
├─ README.md
├─ CHANGELOG.md
├─ ERROR_LOG.md
└─ OUTPUT_MANIFEST.json
```

---

## 11) Baseline Commit Target

Tag:

```text
v0.1.0-leak-rate-static-triage-baseline
```

Commit message:

```text
feat: add leak-rate helium dashboard triage baseline
```

Baseline success means an engineer can open `index.html`, navigate by audience and density, inspect leak-rate calculations, view interactive plots, trace numbers to assumptions/RTM anchors, and determine which valve leak class is justified, excessive, or risky.
