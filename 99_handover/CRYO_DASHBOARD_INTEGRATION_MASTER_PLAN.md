# Cryogenic Dashboard Integration Master Plan

## 1) Purpose and Scope
This document defines the development rules, repository structure, UI style baseline, and engineering model boundaries for co-developing:

- `CODEX` (current working repository)
- `cryo_dashboard_v0_3_0/cryo_dashboard_v0_3_0` (canonical dashboard branch/content)

The intent is to preserve idempotency, avoid uncontrolled dilution of prior working logic, and enforce iterative, reviewable, small-step changes.

---

## 2) Non-Negotiable Development Rules

1. **Small, testable deltas only**
   - Every change must be scoped to a focused unit (UI style, one equation module, one rendering section, one data loader, etc.).
   - Every delta must include a smoke check and a short reviewer note.

2. **Modify-by-proof, not modify-by-assumption**
   - Existing working behavior is baseline truth until replaced by measured or validated behavior.
   - No bulk rewrites without parity verification.

3. **Idempotent outputs**
   - Running generation/build commands repeatedly with the same inputs must produce functionally identical outputs.
   - Generated artifacts should be deterministic (sorted keys, stable ordering, explicit version metadata).

4. **Parallel method retention before convergence**
   - When integrating A/B methods from CODEX and `cryo_dashboard_v0_3_0`, keep both in parallel for one review cycle.
   - Promote one method to default only after comparing:
     - correctness,
     - runtime complexity,
     - render quality,
     - maintainability.

5. **Formal style and visual density control**
   - UI language, labels, and narrative text should be formal engineering style.
   - Must support fast visual review: section anchors, compact cards/tables, clear labels.

---

## 3) Repository Working Structure (Local + GitHub)

### 3.1 Recommended Local Workspace Layout
Create a stable parent folder outside cloud-sync turbulence (e.g., OneDrive live-lock conflicts):

```text
Cryogenic_Engineer_Tools/
  00_upstream/
    CODEX_main_clone/
    cryo_dashboard_v0_3_0_clone/
  10_dev/
    CODEX_dev/
    cryo_dashboard_dev/
  20_stage/
    integration_stage/
  30_release/
    hosted_html_bundle/
```

### Rationale
- `00_upstream`: clean mirrors for diff and reset.
- `10_dev`: active branch work.
- `20_stage`: merge + smoke + regression checks.
- `30_release`: frozen artifacts for local review and host deployment.

## 3.2 Branching and Sync Policy
- Keep `main` protected and releasable.
- Use short-lived branches: `feature/<scope>`, `fix/<scope>`, `integrate/<sourceA>-<sourceB>`.
- For each integration cycle:
  1. Pull latest in both upstream clones.
  2. Rebase or merge into `integration_stage` branch.
  3. Run smoke checks for both legacy and merged flows.
  4. Record decision log (keep A, keep B, or merge hybrid).

---

## 4) UI Theme Baseline (Day/Night + Contrast)

### 4.1 Toggle Requirement
- Provide explicit **Dark/Light mode** toggle.
- Persist user preference (`localStorage` key, e.g., `qet_theme`).
- Default fallback from system preference (`prefers-color-scheme`).

### 4.2 Colour Guidance
Use high contrast as baseline for Windows environments while staying in low-saturation pastel ranges.

#### Heading Palette (SCK-aligned)
- **H1 / H2 Primary:** dark indigo with visible violet tones (must not appear black on light theme).
- Candidate token suggestions:
  - `--heading-primary: #3F2A78` (dark indigo-violet)
  - `--heading-secondary: #5C43A8` (soft deep purple)

#### Accent / Action Palette (replace generic blue default)
- Replace default blue with controlled violet-indigo family:
  - `--accent-default: #6D5BB3`
  - `--accent-hover: #5B4B9A`
  - `--accent-soft-bg: #EEEAFB`

#### Light Theme Surface Tokens
- `--bg: #FAFAFD`
- `--panel: #F3F1FA`
- `--text: #1E1B2E`

### Dark Theme Surface Tokens
- `--bg: #161422`
- `--panel: #211D33`
- `--text: #EEEAFB`

## 4.3 Accessibility Rules
- Body text contrast target: WCAG AA minimum 4.5:1.
- Interactive controls: visible focus ring in both themes.
- Avoid pastel-on-pastel for critical values (warnings must elevate saturation/contrast).

---

## 5) Engineering Model Boundary (Material Properties Subset)

Primary dashboard subset: **Material Properties + Thermal Parasitic Load framing** for cryogenic shield/mass modeling.

### 5.1 Fixed Design Anchors
- Ambient design temperature: `T_ambient = 300 K` (fixed design value).
- Thermal shield nominal stage: `T_shield = 50 K`.
- Cold mass nominal stage: `T_cold_mass = 2 K`.
- Preliminary geometry baseline:
  - Outer cylinder length `L = 3 m`
  - Outer diameter `D_outer = 1.0 m`
  - Inner diameter `D_inner = 0.5 m`

### 5.2 Parasitic Zones
1. `300 K -> 50 K` zone
   - Radiation parasitic load (external to shield).
   - Conduction parasitic load through supports/interfaces.

2. `50 K -> 2 K` zone
   - Residual/intercepted conduction into cold mass.
   - Internal radiation and material-dependent transport.

### 5.3 Radiation Baseline Equation
Use user-supplied empirical constant format for shield load:

```text
Q_rad_50 = Constant_Rad_50 * (300^4 - T_shield^4)
```

For nominal shield stage (`T_shield = 50 K`):

```text
Q_rad_50_nominal = Constant_Rad_50 * (300^4 - 50^4)
```

### 5.4 Conduction/Material Modeling Notes
- Conduction inputs should support mixed materials with temperature-dependent `k(T)` and `cp(T)`.
- Allow enthalpy-based segment integration for cooldown scheduling.
- Cooling-rate plans should support zone bands (`min`, `nominal`, `max`) by time window.

---

## 6) Functional Check Matrix for Integration

For each integration pass, run and document:

1. **Repo structure check**
   - expected directories exist,
   - required manifests present,
   - hostable HTML root available.

2. **Missing-shareable audit**
   - identify files absent in one branch but reusable from the other.

3. **Missing-required audit**
   - identify files that must be created (schema, config, JS module, style tokens, test fixtures).

4. **Dual-run reproducibility**
   - run CODEX method and dashboard method independently,
   - compare outputs,
   - determine convergence strategy.

5. **Human review pass**
   - visual check (theme, contrast, spacing, content density),
   - content check (equation labels, units, anchor values),
   - interaction check (buttons/links/host navigation).

---

## 7) Suggested First Integration Backlog

1. Introduce shared style token file (light/dark + purple/indigo accents).
2. Build minimal thermal parasitic input panel (300/50/2 K anchors editable where allowed).
3. Implement radiation/conduction equation module with explicit unit tags.
4. Add result cards + compact trend table.
5. Add smoke script to verify deterministic HTML build.
6. Add integration decision log template for each cycle.

---

## 8) Definition of Done (Per Iteration)
A change is complete only when:
- unit/smoke checks pass,
- HTML preview is render-stable in both themes,
- baseline equations and constants are visible and labeled,
- integration notes capture what changed and why,
- output can be regenerated without manual patching.
