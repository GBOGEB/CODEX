# Lineage + Full Build/Deploy + CI/CD (One-Cycle Definition)

## Purpose
This playbook defines a **single end-to-end engineering cycle** for this repository, from local clone to validated push, with lineage evidence and CI/CD checkpoints.

## One-Cycle Boundary
A cycle starts when either of the following occurs:

1. Repository is cloned to local Git.
2. A change is pushed from GitHub to source branch (new sync point).

A cycle ends only when all gates below pass and lineage artifacts are updated.

## Cycle Stages (100% Goal)

### 1) Source Synchronization
- Clone/fetch and checkout working branch.
- Confirm clean base and branch protection assumptions.

### 2) Deterministic Environment Setup
- Install dependencies from repository requirements and install the package in editable mode:
  - `python -m pip install -r requirements.txt`
  - `python -m pip install -e .`
- Capture runtime metadata (tool versions) if needed for audit.

### 3) Static + Contract Validation
- Validate repository contracts and metadata:
  - `python scripts/check_manifest.py`
  - `python scripts/check_globs.py`
  - `python scripts/check_links.py`
  - `python scripts/check_stale.py`

### 4) Full Test Build
- Execute full automated tests:
  - `pytest -q`
- Optional focused suites for semantic substrate and render governance (if changed).

### 5) Artifact Build and Packaging
- Rebuild index/package outputs when source data changes:
  - `python -m scripts.build_index --source data/handover_final --output output --dataset-name handover_final`
- Refresh runtime export when required:
  - `python scripts/export_abacus_runtime.py`

### 6) Lineage Recording
- Update operational/runtime evidence when impacted:
  - `OUTPUT_MANIFEST.json`
  - `MANIFEST.json`
  - `meta_runtime/*` evidence files
- Ensure lineage statements reference parent-to-child flow (example: PR-G2 -> PR-H -> PR-H2).

### 7) Commit + Push
- Commit scoped changes with clear message.
- Push branch and open PR.

### 8) CI/CD Enforcement
This repository already has workflow coverage for CI/CD layers in `.github/workflows/`, including:
- Core CI
- Render regression and governance validation
- Semantic validation/runtime pipelines
- GitHub Pages publishing paths

The merge gate should require all applicable workflows to pass before integration.

## Definition of Done (100% Goal)
A cycle is 100% complete when:
- Local checks pass.
- CI checks pass for the PR branch.
- Required artifacts/manifests are regenerated and committed.
- Lineage evidence is updated and reviewable.
- Branch is merged or accepted according to governance rules.

### Incomplete/Stub Code Gate (Required before cycle close)
- If `pytest -q` fails during collection, treat the cycle as incomplete and capture the blocker in lineage notes.
- Current known blockers and framework gaps:
  - `src/gistau_ch15/visualization/pages_artifact_refresh.py` currently has a malformed/duplicated `refresh(...)` method signature block that prevents full test collection.
  - Framework stubs are present in `src/gistau_ch15/kernels/saturation_stub.py` and `semantic_substrate/engines/delta_extractor.py`.
- Track missing buildout work in the repository TODO plans:
  - `handover/GISTAU_CH15_TECH_TODO_IMPLEMENTATION_PLAN.md`
  - `handover/GISTAU_CH15_V11_STUDY_AND_TODO.md`

## Recommended Operator Command Bundle
```bash
python -m pip install -r requirements.txt
python -m pip install -e .
python scripts/check_manifest.py
python scripts/check_globs.py
python scripts/check_links.py
python scripts/check_stale.py
pytest -q
```

Use this bundle as the baseline pre-push gate for every cycle.
