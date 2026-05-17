# GISTAU Chapter 15 v12 — Static HTML Publication Convergence Status

## Purpose

This iteration collates the major development steps from v8 through v11 and converts them into a clear convergence plan for a published static HTML engineering portal.

Target repository context:

- Requested: `GBOGEN/CODEX`
- Accessible through GitHub connector: `GBOGEB/CODEX`
- Active branch created: `ch15-v11-recursive-engineering`
- Existing handover file: `handover/GISTAU_CH15_V11_PR_HANDOVER.md`

---

# 1. Major Development Lineage

## v8 — Visual / Proof Iteration

### Achieved
- Main HTML reader
- Workbook v8
- Source preview rendering
- OCR-assisted source split
- Source preview PDF
- Main process SVG
- Thermodynamic static plots: T-s, 1/T-s, rho / specific-volume dual-axis
- Separate plot pages: compressor, JT valve, heat exchanger, equivalent power
- Workbook sheets: Main_Calc_Table, Reproduction_Tests, OCR_Source_Split, Plot_* sheets, Links

### Regression risk found
- Some HTML/Plotly pages appeared stale or inactive from sandbox links.
- CDN dependency and static file linkage were fragile.

## v9 — Active Self-contained Rebuild

### Achieved
- Self-contained HTML portal
- Inline JavaScript/SVG plotting
- No CDN dependency
- Active plot console
- Main process diagram
- Active thermo plots
- Active rho/v plots
- GitHub-friendly static layout

### Regression risk found
- Stronger active behavior, but less content depth than v8.
- Needed recursive inheritance instead of replacement.

## v10 — Plot Regression Fix

### Achieved
- Dense 2D/3D engineering plots
- Compressor ranking curves
- Equivalent-power ranking curves
- 3D compressor surface
- 3D equivalent-power wireframe
- T-s cold/hot focus
- rho/v dual-axis plot
- Static PNG plot backups

### Regression risk found
- Plot quality improved, but this was not fully integrated with workbook/OCR/source lineage.

## v11 — Recursive Engineering Reconstruction

### Achieved
- Recursive HTML engineering portal
- v8/v9/v10 lineage register
- Control workbook
- Python engine
- Python tests
- Active SVG/JS plot engine
- Static plot backups
- OCR/source split register
- REFPROP adapter stub
- HEPAK adapter stub
- DMAIC/TODO tracker
- 7 critical TODOs
- Codex handover
- GitHub branch handover pushed to `GBOGEB/CODEX`

### Validation status
- Python tests: passed
- Workbook formula scan: clean
- Active HTML: generated
- Static plot backup: generated
- GitHub handover: created

---

# 2. Current Publication Status

| Area | Status | Notes |
|---|---:|---|
| `index.html` portal | READY-CANDIDATE | Needs placement under publish folder |
| `styles.css` | READY | No external dependency |
| `active_v11.js` | READY | Embedded data + self-contained SVG renderer |
| `assets/diagrams/*.svg` | READY | Main and per-domain diagrams |
| `assets/static_plots/*.png` | READY | Static fallback plots |
| `plots/*.html` | READY-CANDIDATE | Separate active plot pages |
| `data/*.json` | READY | Tuple/surface/TODO/source registers |
| Workbook | REVIEW ARTIFACT | Downloadable artifact |
| PDF previews | REVIEW ARTIFACT | Downloadable artifact |
| Python engine | DEVELOPMENT ARTIFACT | CI validation / reproducibility |
| Tests | DEVELOPMENT ARTIFACT | CI validation |
| REFPROP/HEPAK exact values | NOT READY | Explicit TODO |

---

# 3. Recommended Published HTML Layout

Use a GitHub Pages-compatible structure:

```text
docs/
  gistau-ch15/
    index.html
    styles.css
    active_v11.js
    assets/
      diagrams/
      static_plots/
      source_pages/
    plots/
    data/
    downloads/
      GISTAU_Chapter15_v11_Recursive_Workbook.xlsx
      source_preview_ocr_split_v11.pdf
    tools/
      cryo_toolbox_v11.py
      test_cryo_toolbox_v11.py
```

Expected public URL after GitHub Pages activation:

```text
https://gbogeb.github.io/CODEX/gistau-ch15/
```

---

# 4. Publication Gates

## Gate 1 — Required files

```text
docs/gistau-ch15/index.html
docs/gistau-ch15/styles.css
docs/gistau-ch15/active_v11.js
docs/gistau-ch15/data/tuple_registry.json
docs/gistau-ch15/data/surface_data.json
docs/gistau-ch15/data/critical_todos.json
docs/gistau-ch15/plots/thermo_active.html
```

## Gate 2 — Link integrity

Check:
- all local `href=` links resolve
- all local `src=` links resolve
- all `object data=` SVG links resolve
- no CDN dependencies
- no absolute sandbox links remain
- no missing `assets/` paths

## Gate 3 — Data integrity

```bash
python -m json.tool docs/gistau-ch15/data/tuple_registry.json
python -m json.tool docs/gistau-ch15/data/surface_data.json
python -m json.tool docs/gistau-ch15/data/critical_todos.json
```

## Gate 4 — Python validation

```bash
python docs/gistau-ch15/tools/test_cryo_toolbox_v11.py
```

## Gate 5 — Publication smoke test

Open locally:

```text
docs/gistau-ch15/index.html
```

Verify:
- main diagram visible
- active plot console draws
- T-s plot draws
- rho/v plot draws
- separate plot pages open
- workbook download link works
- source preview PDF link works

---

# 5. Seven Critical TODOs Remaining

These remain explicit engineering blockers and should not block static publication if visibly tracked.

1. TODO-01 — REFPROP adapter integration
2. TODO-02 — HEPAK adapter integration
3. TODO-03 — Manual transcription of canonical example values
4. TODO-04 — True helium phase boundary reconstruction near 1.8 K
5. TODO-05 — Exact vector recreation of canonical figures/tables
6. TODO-06 — Saturation dome and two-phase region reconstruction
7. TODO-07 — Engineering-grade validation against canonical examples

---

# 6. Clear Next Execution Steps

## Step 1 — Create publication folder

```bash
mkdir -p docs/gistau-ch15
```

Copy the v11 portal contents into:

```text
docs/gistau-ch15/
```

Preserve relative paths.

## Step 2 — Add CI workflow

Create:

```text
.github/workflows/gistau-ch15-static-html.yml
```

Minimum workflow:

```yaml
name: gistau-ch15-static-html

on:
  push:
    paths:
      - 'docs/gistau-ch15/**'
      - '.github/workflows/gistau-ch15-static-html.yml'
  pull_request:
    paths:
      - 'docs/gistau-ch15/**'
      - '.github/workflows/gistau-ch15-static-html.yml'

jobs:
  validate-static-html:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Validate required files
        run: |
          test -f docs/gistau-ch15/index.html
          test -f docs/gistau-ch15/styles.css
          test -f docs/gistau-ch15/active_v11.js
          test -f docs/gistau-ch15/data/tuple_registry.json
          test -f docs/gistau-ch15/data/surface_data.json
          test -f docs/gistau-ch15/data/critical_todos.json
          test -f docs/gistau-ch15/plots/thermo_active.html

      - name: Validate JSON registers
        run: |
          python -m json.tool docs/gistau-ch15/data/tuple_registry.json > /dev/null
          python -m json.tool docs/gistau-ch15/data/surface_data.json > /dev/null
          python -m json.tool docs/gistau-ch15/data/critical_todos.json > /dev/null

      - name: Detect forbidden external dependencies
        run: |
          ! grep -R "cdn.plot.ly\\|https://cdn\\|sandbox:" docs/gistau-ch15

      - name: Validate Python tests if present
        run: |
          if [ -f docs/gistau-ch15/tools/test_cryo_toolbox_v11.py ]; then
            python docs/gistau-ch15/tools/test_cryo_toolbox_v11.py
          fi
```

## Step 3 — Add publication README

Create:

```text
docs/gistau-ch15/README.md
```

## Step 4 — Open PR

Suggested PR title:

```text
feat: publish GISTAU chapter 15 recursive static engineering portal
```

---

# 7. Convergence Definition

The portal is considered converged to published static HTML when:

1. PR is open against `main`.
2. CI passes.
3. `docs/gistau-ch15/index.html` opens from GitHub Pages.
4. Active plots render without external dependencies.
5. Workbook/PDF download links work.
6. 7 critical TODOs are visible in the portal.
7. No claims of exact REFPROP/HEPAK reproduction are made until TODOs close.

---

# 8. Recommended PR Split

## PR 1 — Static portal publication
- `docs/gistau-ch15/**`
- CI workflow
- README

## PR 2 — Python package hardening
- package structure
- tests
- pyproject integration

## PR 3 — REFPROP/HEPAK adapter work
- optional dependency design
- adapter interface
- mocked tests

## PR 4 — Source transcription
- canonical examples CSV
- OCR cleanup
- figure/table value capture

## PR 5 — Engineering validation
- real helium phase boundaries
- saturation dome
- validated reproduction reports

---

# 9. Immediate Instruction for Codex / Copilot

```text
Continue from branch `ch15-v11-recursive-engineering`.

Create `docs/gistau-ch15/` and move/copy the generated v11 static portal package into it.

Keep all links relative.
Do not use CDN dependencies.
Do not remove TODOs.
Add GitHub Actions validation.
Open a PR titled:
`feat: publish GISTAU chapter 15 recursive static engineering portal`.

Use the existing handover:
`handover/GISTAU_CH15_V11_PR_HANDOVER.md`.

Add this v12 convergence status as:
`handover/GISTAU_CH15_V12_PUBLISH_HTML_STATUS.md`.
```
