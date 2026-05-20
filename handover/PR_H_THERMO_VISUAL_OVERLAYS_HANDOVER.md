# PR-H Thermodynamic Visual Overlays Handover

## Status

Draft PR package prepared from the merged PR-G2 backend governance baseline.

## Purpose

PR-H introduces the first rendered thermodynamic visualization layer for GISTAU Chapter 15.

The immediate goal is to make the visual review pipeline viable before connecting live backend-generated datasets from CoolProp, REFPROP, and HEPAK.

## Branch

```text
pr-h-thermo-visual-overlays
```

## Baseline

PR-G2 was merged and established:

- optional backend adapter scaffolds,
- backend availability reporting,
- comparison runner scaffolding,
- GitHub Pages review artifacts,
- CI-safe optional backend rules.

PR-H builds on this by adding rendered visualization surfaces.

## Added Artifacts

### Data

```text
docs/gistau-ch15/data/thermo_visual_overlay_seed.json
```

Contains deterministic scaffold data for:

- saturation dome overlay,
- T-s reconstruction,
- low-temperature phase map,
- backend delta overlay,
- cryogenic expander validation,
- backend agreement heatmap.

### Plotly Dashboard

```text
docs/gistau-ch15/plots/thermo_visual_overlays.html
```

Renders six interactive Plotly panels:

1. Saturation Dome Overlay
2. T-s Reconstruction
3. Low-Temperature Phase Map
4. Backend Delta Overlay
5. Cryogenic Expander Validation
6. Backend Agreement Heatmap

### Portal Link

```text
docs/gistau-ch15/index.html
```

Adds a direct link to:

```text
plots/thermo_visual_overlays.html
```

## Review Notes

The present dataset is deterministic and intentionally non-canonical. It validates rendering, data schema, dashboard plumbing, and GitHub Pages integration.

It must not be treated as final REFPROP or HEPAK thermodynamic truth.

## Engineering Meaning

PR-H moves the project from backend governance into visual validation infrastructure.

It creates the correct review surface for later real data overlays:

- CoolProp live surfaces,
- REFPROP canonical comparisons,
- HEPAK low-temperature helium surfaces,
- saturation dome physics,
- T-s cycle reconstruction,
- backend agreement heatmaps.

## Acceptance Criteria

- GitHub Pages portal links to the PR-H dashboard.
- Dashboard loads JSON data from docs/gistau-ch15/data.
- Six review panels render without a build step.
- Data schema can later be replaced by generated backend output.
- No licensed backend is required for CI or static Pages preview.

## Deferred To Next PRs

### PR-H2: Live Data Generator

- Add Python generator for thermo_visual_overlay_seed.json.
- Generate saturation dome samples from available backends.
- Use fallback when optional engines are unavailable.

### PR-H3: CoolProp Surface Binding

- Use CoolPropAdapter when installed.
- Generate real saturation curves and T-s paths.
- Compare fallback against CoolProp.

### PR-H4: REFPROP/HEPAK Canonical Overlay

- Connect local REFPROP runtime when configured.
- Connect local HEPAK bridge when configured.
- Produce 2 K helium validation overlays.

### PR-I: Publication Validation Package

- Export workbook-ready delta tables.
- Add tolerance bands.
- Add provenance metadata.
- Add static PNG exports for reports.

## Codex Next Instructions

1. Keep optional backend safety intact.
2. Do not make CoolProp, REFPROP, or HEPAK mandatory in CI.
3. Treat seed JSON as visualization scaffolding only.
4. Add generated data in docs/gistau-ch15/data for Pages visibility.
5. Keep plots self-contained and reviewable from GitHub Pages.
6. Prefer small generator modules with deterministic fallback paths.

## Suggested Next Files

```text
src/gistau_ch15/visualization/thermo_overlay_generator.py
src/gistau_ch15/visualization/saturation_sampling.py
src/gistau_ch15/visualization/ts_reconstruction.py
src/gistau_ch15/visualization/backend_agreement.py
tests/gistau_ch15/test_thermo_visual_overlay_generator.py
```

## Suggested Next Commit Sequence

```text
1. Add visualization generator package
2. Add fallback saturation sampler
3. Add T-s reconstruction sampler
4. Add backend agreement matrix builder
5. Add generated JSON refresh command
6. Add CI-safe generator tests
```
