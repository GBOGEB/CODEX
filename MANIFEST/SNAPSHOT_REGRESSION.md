# SNAPSHOT REGRESSION GOVERNANCE

## Purpose

Introduce deterministic render-regression review for:

- HTML
- PDF
- PPTX
- GitHub Pages snapshots

---

## Target Validation Areas

### Layout Stability

Detect:

- title clipping
- card overflow
- inconsistent spacing
- semantic drift
- navigation displacement

---

### Theme Stability

Detect:

- dark/light semantic regressions
- inaccessible contrast
- semantic card transform failures

---

### Navigation Stability

Detect:

- broken anchors
- invalid next/previous navigation
- figure-reference drift
- registry mismatch

---

## Future Snapshot Workflow

```text
RENDER
  ↓
SNAPSHOT
  ↓
BASELINE COMPARISON
  ↓
REGRESSION DELTA
  ↓
CI PASS/FAIL
```

---

## Planned Tooling

Future planned tooling:

```text
renderers/regression/
├── snapshot_diff.py
├── screenshot_compare.py
├── html_baseline_compare.py
└── pdf_visual_compare.py
```

---

## Future CI Integration

Planned GitHub Actions integration:

- automatic snapshot generation
- screenshot comparisons
- render delta uploads
- GitHub Pages regression review

---

## Governance Principle

Renderer quality must become:

```text
measurable and reproducible
```

not:

```text
subjective visual inspection only
```
