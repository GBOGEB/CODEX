# GISTAU Chapter 15 v11 — Codex / Copilot PR Handover

## Repository
- Target repo: `GBOGEB/CODEX`
- Requested alias from user: `GBOGEN/CODEX` (not found via GitHub connector)
- Working branch: `ch15-v11-recursive-engineering`
- Base branch: `main`

## Mission
Integrate the generated v11 recursive cryogenic engineering reconstruction package into the CODEX repository without regression or dilution.

The package consolidates:
- v8 visual/proof lineage
- v9 active self-contained HTML
- v10 dense 2D/3D engineering plots
- v11 recursive orchestration

## Core Deliverables
1. Recursive engineering HTML portal
2. Control workbook
3. Python calculation engine
4. Active SVG/JS plot engine
5. OCR/source split registry
6. REFPROP/HEPAK adapter scaffolds
7. DMAIC + TODO traceability
8. Validation/idempotency tests

## Generated Local Artifacts
- GISTAU_Chapter15_v11_RECURSIVE_ENGINEERING_RECONSTRUCTION.zip
- gistau_ch15_v11_recursive/index.html
- gistau_ch15_v11_recursive/GISTAU_Chapter15_v11_Recursive_Workbook.xlsx
- gistau_ch15_v11_recursive/tools/cryo_toolbox_v11.py
- gistau_ch15_v11_recursive/tools/test_cryo_toolbox_v11.py
- gistau_ch15_v11_recursive/docs/CODEX_HANDOVER.md

## Recommended Repository Layout
```text
codex/
  cryogenic/
    gistau_ch15/
      portal/
      workbook/
      tools/
      data/
      assets/
      plots/
      docs/
      tests/
```

## GitHub Copilot Session Prompt
```text
You are integrating a recursive cryogenic engineering reconstruction framework.

Goals:
- Preserve v8/v9/v10 lineage
- Avoid regression/dilution
- Keep HTML self-contained
- Preserve workbook structure
- Preserve active SVG plots
- Maintain idempotent tests
- Prepare CI workflows

Required:
- Python 3.11+
- pytest/unittest support
- artifact integrity checks
- static HTML validation
- JSON schema validation
- ZIP artifact generation

Critical TODOs:
TODO-01 REFPROP adapter
TODO-02 HEPAK adapter
TODO-03 canonical example transcription
TODO-04 helium phase boundary reconstruction
TODO-05 vector recreation of canonical figures
TODO-06 saturation dome reconstruction
TODO-07 engineering-grade validation
```

## Recommended CI Pipeline
### Stage 1
- lint python
- validate JSON
- validate workbook exists
- validate HTML exists

### Stage 2
- run `python tools/test_cryo_toolbox_v11.py`
- validate idempotency hashes
- validate no formula scan errors

### Stage 3
- generate release ZIP
- upload artifacts

## Suggested GitHub Actions
```yaml
name: gistau-v11
on:
  push:
  pull_request:
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: python -m pip install -U pip
      - run: python tools/test_cryo_toolbox_v11.py
```

## Suggested Commit Sequence
1. scaffold + lineage
2. workbook integration
3. active html/svg plots
4. static plots + thermo
5. OCR/source split
6. tests + validation
7. CI/CD workflows
8. PR finalization

## Suggested PR Title
`feat: add GISTAU chapter 15 recursive cryogenic engineering reconstruction v11`

## Suggested PR Labels
- engineering
- cryogenics
- thermodynamics
- visualization
- html
- workbook
- validation
- codex

## Suggested PR Body
### Summary
Adds the v11 recursive engineering reconstruction framework for GISTAU chapter 15.

### Includes
- active HTML engineering portal
- recursive workbook
- SVG/JS plots
- OCR/source split
- Python calc engine
- DMAIC/TODO tracking
- validation/idempotency tests

### Validation
- Python tests pass
- workbook formula scan clean
- active plots self-contained

### Known Blockers
- REFPROP integration pending
- HEPAK integration pending
- exact canonical validation pending

## Integration Notes
- Prefer incremental PRs over large binary drops.
- Preserve prior lineage artifacts.
- Never replace a working artifact without superseding metadata.
- Keep plot rendering offline/self-contained.
