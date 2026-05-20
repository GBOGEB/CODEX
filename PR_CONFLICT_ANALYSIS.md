# PR Conflict Analysis & Resolution TODO

**Repository:** GBOGEB/CODEX
**Prepared by:** Copilot coding agent
**Date:** 2026-05-20
**Branch:** `copilot/fix-open-issues-and-pr-conflicts`

---

## Executive Summary

Three open pull requests (#90, #92, #97) cannot be merged cleanly into
`main`.  The root causes are:

1. **Stale base commits** — PR #92 and PR #97 were branched from older `main`
   commits.  Subsequent merges into `main` added or modified files that these
   PRs also touch.
2. **Overlapping MANIFEST edits** — All three PRs modify `MANIFEST/RENDER_RULES.md`
   and `MANIFEST/STYLE_GUIDE.md` with different content.  They cannot be
   auto-merged by GitHub.
3. **Scope entanglement** — PR #92 (`a6-render-governance`) is very large
   (~100 files) and re-introduces files that are already present on `main`
   from previous merges, creating three-way merge conflicts.

---

## PR-by-PR Findings

### PR #90 — A6: Renderer governance layer and ABACUS render pipeline manifests

| Field | Value |
|---|---|
| Branch | `a6-renderer-governance-layer` |
| Base commit | `9279dcbb` (= current `main` HEAD) |
| Status | Cannot merge — conflict on MANIFEST files with PRs #92 |
| Conflicting files | `MANIFEST/RENDER_RULES.md`, `MANIFEST/STYLE_GUIDE.md` |

**Root cause:** PR #90 modifies `MANIFEST/RENDER_RULES.md` and
`MANIFEST/STYLE_GUIDE.md`, which are also modified by PR #92 with different
content.  Additionally, this PR adds `MANIFEST/CHANGELOG.md`,
`MANIFEST/README.md`, `MANIFEST/README_MAX.md`, and
`MANIFEST/SESSION_OFFLOAD_PR_G2_A6.md`.

**What was done in this PR (this branch):**
- `MANIFEST/CHANGELOG.md`, `MANIFEST/README.md`, `MANIFEST/README_MAX.md`
  have been cherry-picked from PR #90 and committed to this branch, resolving
  the missing-manifest-files portion of Issue #89.

**Resolution TODO for PR #90:**
- [ ] Confirm the MANIFEST/RENDER_RULES.md and MANIFEST/STYLE_GUIDE.md edits
      in PR #90 are the canonical/preferred versions.
- [ ] If so, close PR #92 (see below) and merge PR #90 first.
- [ ] Alternatively, update MANIFEST/RENDER_RULES.md and MANIFEST/STYLE_GUIDE.md
      on `main` with the A6 governance content and close both PR #90 and PR #92,
      since the MANIFEST files they add now live on `main` via this PR.

---

### PR #92 — A6: renderer governance and semantic theme contracts

| Field | Value |
|---|---|
| Branch | `a6-render-governance` |
| Base commit | `b7d38cc4` (stale — several merges behind `main`) |
| Status | Cannot merge — stale base + conflicts on ~10 files |
| Conflicting files | `MANIFEST/CHANGELOG.md`, `MANIFEST/RENDER_RULES.md`, `MANIFEST/STYLE_GUIDE.md`, `.github/workflows/ci.yml`, `.github/copilot-instructions.md`, `MANIFEST.json`, and others |

**Root cause:** PR #92 was based on `b7d38cc4`.  Since then, `main` received
multiple merges (PRs #88, #89, #95) that added or changed:
- `MANIFEST/RENDER_RULES.md` and `MANIFEST/STYLE_GUIDE.md` (different A6
  content than PR #92 proposes),
- `.github/workflows/ci.yml`, `.github/copilot-instructions.md`,
- `MANIFEST.json`,
- and many `docs/gistau-ch15/`, `governance/`, `src/gistau_ch15/`,
  `semantic_substrate/` files.

**Resolution TODO for PR #92:**
- [ ] **Option A (Recommended — Rebase):** Rebase `a6-render-governance` onto
      current `main`:
      ```bash
      git fetch origin main
      git checkout a6-render-governance
      git rebase origin/main
      # Resolve conflicts file-by-file
      ```
      Key conflict decisions:
      - `MANIFEST/RENDER_RULES.md` — keep the `main` version (A6 governance
        rules) and integrate only the PR #92 additions that are not already
        present.
      - `MANIFEST/STYLE_GUIDE.md` — same strategy.
      - `MANIFEST/CHANGELOG.md` — `main` now has this file; merge the
        PR #92 version to append/update, don't replace.
      - `governance/*.py` — accept PR #92 additions wholesale (they add new
        files that don't conflict with `main` content).
      - `.github/workflows/ci.yml` and `.github/copilot-instructions.md` —
        inspect each diff and choose `main` version unless PR #92 adds
        genuinely new functionality.
- [ ] **Option B (Close & Re-open):** Close PR #92.  Create a fresh branch
      from current `main`, cherry-pick only the unique commits from
      `a6-render-governance` that are not already on `main`, and open a new
      narrow PR.
- [ ] After resolution, validate CI:
      ```bash
      python -m pytest -q
      python scripts/check_manifest.py
      python scripts/check_globs.py
      python scripts/check_stale.py
      python scripts/check_links.py
      ```

---

### PR #97 — Add generated overlay pipeline and manifest

| Field | Value |
|---|---|
| Branch | `codex/document-pr-h2-architectural-changes` |
| Base commit | `92def4c9` (stale — multiple merges behind `main`) |
| Status | Cannot merge — stale base + conflicts on shared visualization/governance files |
| Conflicting files | `MANIFEST/RENDER_RULES.md`, `MANIFEST/STYLE_GUIDE.md`, `governance/WCAG_CONTRAST_CHECKER.py`, `governance/SLIDE_ID_ENFORCER.py`, `src/gistau_ch15/visualization/pages_artifact_refresh.py`, `src/gistau_ch15/visualization/regenerate_overlay_json.py`, `tests/gistau_ch15/test_visualization_scaffolds.py`, `.github/workflows/ci.yml`, `.github/copilot-instructions.md` |

**Root cause:** PR #97 is based on `92def4c9`.  Since then, `main` merged
several branches that already incorporated most of the visualization and
governance changes PR #97 proposes.  Specifically, the files
`src/gistau_ch15/visualization/overlay_artifact_manifest.py`,
`src/gistau_ch15/visualization/refresh_overlay_artifacts.py`, and
`tests/gistau_ch15/test_refresh_overlay_artifacts.py` were already merged into
`main` before PR #97 was opened, meaning PR #97 re-introduces identical or
conflicting versions.

**Resolution TODO for PR #97:**
- [ ] Run `git diff main..codex/document-pr-h2-architectural-changes` and
      identify any commits in PR #97 that are NOT already on `main`.
- [ ] If all material changes are already on `main`, close PR #97 as
      "superseded" with a comment citing the merge that included the work.
- [ ] If there are genuinely new additions (e.g., `README.md` updates,
      new data fixtures), cherry-pick only those commits onto a clean branch
      from current `main`.
- [ ] Pay attention to `docs/gistau-ch15/data/generated_overlay_manifest.json`
      — if `main` has a more recent version this file should NOT be regressed.

---

## Inter-PR Dependency Map

```
main (HEAD: 9279dcbb)
 ├── PR #90  [a6-renderer-governance-layer]  — base = main HEAD ✓
 │   touches: MANIFEST/*.md, .github/workflows/semantic-validation.yml
 │
 ├── PR #92  [a6-render-governance]          — base = b7d38cc4 (stale) ✗
 │   touches: MANIFEST/*.md + ~90 more files
 │   CONFLICTS WITH: PR #90 (MANIFEST files), main (most files)
 │
 └── PR #97  [codex/document-pr-h2-...]     — base = 92def4c9 (stale) ✗
     touches: MANIFEST/*.md + visualization + governance
     CONFLICTS WITH: PR #92, main (shared viz/governance files)
```

**Recommended merge order (if rebasing):**

1. Merge PR #90 (narrowest, base already at HEAD).
2. Rebase and merge PR #97 (visualization/overlay pipeline additions).
3. Rebase and merge PR #92 (broad semantic/render governance), resolving
   any remaining conflicts from steps 1–2.

---

## Shared Conflict File Quick Reference

| File | PR #90 | PR #92 | PR #97 | Action |
|---|---|---|---|---|
| `MANIFEST/RENDER_RULES.md` | Modified (expanded A6 rules) | Modified (governance spec) | Modified (same as #92 base) | Keep the most complete version; currently main has the minimal version — PR #90's expanded version is preferred |
| `MANIFEST/STYLE_GUIDE.md` | Modified (full semantic cards + typography) | Modified (guide-as-language spec) | Modified | Keep PR #90 version (comprehensive YAML examples); merge PR #92's language guidance as an addendum |
| `MANIFEST/CHANGELOG.md` | Added (new) | Added (new, different content) | Not touched | PR #90 version now on `main` via this branch; PR #92's changelog can be merged/appended |
| `.github/workflows/ci.yml` | Not touched | Modified | Modified | Inspect diff; accept only genuine new steps |
| `.github/copilot-instructions.md` | Not touched | Modified | Modified | Accept whichever has the correct CI command list |
| `governance/WCAG_CONTRAST_CHECKER.py` | Not touched | Adds new file | Not touched | PR #92 adds this file; accept wholesale |
| `governance/SLIDE_ID_ENFORCER.py` | Not touched | Adds new file | Modifies | Inspect for conflicts |
| `src/gistau_ch15/visualization/pages_artifact_refresh.py` | Not touched | Modified | Modified | `main` already has the PR-H2 version; prefer `main` |

---

## Open Issues Addressed in This PR

| Issue | Status | Notes |
|---|---|---|
| #89 A6 Renderer Governance | ✅ Partial | Added `MANIFEST/CHANGELOG.md`, `MANIFEST/README.md`, `MANIFEST/README_MAX.md`. `RENDER_RULES.md` and `STYLE_GUIDE.md` already on `main`. Full A6 linting engine remains TODO. |
| #71 PR-H4 equation kernels | ✅ Done | Added `helium_reference.py` and `saturation_curves.py` kernels + 34 tests. |
| #83 PR-G2 numerical validation pass | 🔶 Scaffold | Backend infrastructure is on `main` (frontier_runner, comparison_runner, etc.). Numerical coupling to REFPROP/HEPAK requires licensed backends. See below. |
| #57 PR-G live property backend | 🔶 Scaffold | `backend_selector.py`, `comparison_runner.py`, `json_export.py` all exist on `main`. Delta heatmap HTML and numerical baselines require backend execution. |
| #76 Phase 3 Semantic Runtime | 📋 Documented | `semantic_substrate/` directory exists with runtime YAML and Python files. Full operationalization is a multi-PR effort. See `PHASE_ROADMAP.md`. |
| #81 Phase 4 Autonomous Cognition | 📋 Documented | Depends on Phase 3 completion. See `PHASE_ROADMAP.md`. |

---

## TODO: Remaining Work (Not Implemented in This PR)

### Issue #89 — A6 Renderer Governance
- [ ] Implement `governance/contrast_lint.py` (WCAG automated checker)
- [ ] Implement `governance/overflow_lint.py`
- [ ] Implement `governance/spacing_lint.py`
- [ ] Add `MANIFEST/MASTER_SLIDE_REGISTRY.yaml`
- [ ] Add `MANIFEST/MASTER_FIGURE_REGISTRY.yaml`
- [ ] HTML/PDF snapshot regression testing

### Issue #71 — PR-H4 Equation Kernels
- [ ] `src/gistau_ch15/kernels/helium_reference.py` ✅ Done
- [ ] `src/gistau_ch15/kernels/saturation_curves.py` ✅ Done
- [ ] `src/gistau_ch15/kernels/he_ii_region.py` — He-II lambda-region kernel
- [ ] `src/gistau_ch15/kernels/jt_inversion.py` — Joule-Thomson inversion line
- [ ] Integration of kernels with CoolProp adapter for comparison
- [ ] NIST numerical regression baseline tests (requires NIST WebBook data fixtures)

### Issue #83 — PR-G2 Numerical Validation
- [ ] Run `python -m gistau_ch15.properties.frontier_runner` with CoolProp available
- [ ] Populate `docs/gistau-ch15/data/backend_comparison_report.json` with real values
- [ ] Generate `docs/gistau-ch15/data/backend_delta_summary.json`
- [ ] REFPROP numerical regression baselines (requires REFPROP license)
- [ ] HEPAK wetness validation (requires HEPAK license)

### Issue #57 — PR-G Live Property Backend
- [ ] Execute `worked_examples.json` → `comparison_runner.py` → JSON reports pipeline
- [ ] Generate `docs/gistau-ch15/backend_delta_heatmap.html`
- [ ] Verify `docs/gistau-ch15/data/backend_availability.json` is accurate

### Issues #76 / #81 — Semantic Runtime
- [ ] Implement `semantic_substrate/runtime/orchestration_loop.py` replay harness
- [ ] Add `semantic_substrate/engines/drift_execution_engine.py`
- [ ] Phase 4 autonomous correction engine
- [ ] Persistent semantic memory layer
