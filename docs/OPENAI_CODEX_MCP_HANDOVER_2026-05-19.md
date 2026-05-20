# OpenAI Codex MCP Handover — Recursive Idempotent Engineering Method

**Date:** 2026-05-19  
**Repository:** `GBOGEB/CODEX`  
**Purpose:** Cloud/IDE handover for OpenAI Codex, MCP-assisted workflows, and future continuation of the Cryogenic Material Dashboard / ABACUS-style recursive engineering automation.

---

## 1. Executive Summary

This document captures the current recursive and idempotent methodology requested by GBOGEB for use inside Codex, VS Code, GitHub, and any future MCP/cloud-connected coding environment.

The key objective is to prevent uncontrolled "vibe coding" drift by separating:

```text
Thinking -> extraction, comparison, planning, documentation
Doing    -> one scoped implementation change only
Control  -> regression, baseline comparison, changelog, handover
```

The working principle is:

```text
Same input + same baseline + same instruction contract = same output
```

The methodology is intended for engineering-grade artefacts where numerical logic, traceability, and release integrity matter more than uncontrolled feature velocity.

---

## 2. Current Project Context

The immediate project context is the Cryogenic Material Dashboard and associated recursive development workflow.

Known active baseline from previous handover:

```text
Branch: feature/method-comparison-panel
Version: v0.4.5
Commit: 95feba55199f995dd5a3739a1bc1e8f374bb4d82
```

Baseline capabilities:

```text
- 10 NIST cryogenic materials
- k(T) and cp(T) support
- Ti-6Al-4V k-only condition retained
- Trapezoid integration
- Simpson integration
- Romberg integration
- Gauss-Legendre 4-point integration
- Single Method and Compare All modes
- Delta Summary panel
- CSV export
- JSON export
- PNG plot export
```

This baseline must be treated as locked unless an explicit engineering-change task authorizes modification.

---

## 3. Absolute Control Rule

Codex must not merge multiple conceptual changes in one iteration.

Never allow this combination in one task:

```text
visual changes
+ equation changes
+ export changes
+ method changes
+ refactor changes
```

This is the primary source of recursive corruption.

Every task must answer:

```text
1. What exact input changed?
2. What exact output is expected?
3. What baseline must remain unchanged?
4. What test proves no regression occurred?
5. What artefact is now authoritative?
```

---

## 4. Source of Truth Hierarchy

Use this hierarchy before editing any code.

```text
LEVEL 0 — Immutable References
--------------------------------
- NIST equations
- BAS equations
- validated reference CSVs
- original raw engineering source data

LEVEL 1 — Locked Engineering Baseline
-------------------------------------
- v0.4.5 validated outputs
- regression fixtures
- golden outputs
- known accepted method deltas

LEVEL 2 — Runtime Implementation
--------------------------------
- js/*.js
- dashboard_modular.html
- state logic
- plots logic
- export logic

LEVEL 3 — Visual / UI Layer
---------------------------
- style.css
- labels
- tooltips
- theme
- dashboard layout

LEVEL 4 — Experimental / Future Hooks
-------------------------------------
- new numerical methods
- uncertainty propagation
- Monte Carlo
- multi-stage thermal intercept model
- optimization
- ABACUS-style workflow extensions
```

Rule:

```text
A lower-trust layer must never silently overwrite a higher-trust layer.
```

Example:

```text
UI text must not redefine engineering meaning.
Experimental methods must not overwrite locked baselines.
```

---

## 5. Change Classification System

Each Codex task must be tagged before implementation.

Recommended file:

```text
CHANGE_CLASSIFICATION.md
```

Classification table:

| Type | Meaning | Typical Files | Required Control |
|---|---|---|---|
| E1 | Engineering calculation | `js/materials.js`, formulas | baseline comparison + review |
| E2 | Numerical method | `js/numerics.js` | regression + golden comparison |
| E3 | Material source data | `data/materials.json` | source citation + schema validation |
| V1 | Visual only | `style.css`, labels | no numerics changes |
| V2 | UX only | `dashboard_modular.html`, UI controller | no equation changes |
| X1 | Export only | `js/export.js` | UI/export consistency test |
| T1 | Test only | `tests/*` | no production output changes |
| D1 | Documentation only | `docs/*`, `README.md` | no app logic changes |
| R1 | Release governance | `VERSION`, changelog, manifest | tests must already pass |
| A1 | Automation / ABACUS | scripts, generators, RTM | dry-run first |

Guardrails:

```text
E-type changes require regression testing.
V-type changes cannot touch numerics.js.
T-type changes cannot modify production outputs.
D-type changes cannot alter runtime files.
R-type changes only occur after validation.
```

---

## 6. Codex Execution Modes

Codex should be run in one explicit mode per interaction.

### MODE A — THINKING

Allowed:

```text
- analysis
- comparison
- proposal
- documentation
- RTM extraction
- task queue generation
```

Forbidden:

```text
- code modification
- file rewrites
- refactor
```

### MODE B — IMPLEMENTATION

Allowed:

```text
- one scoped task
- smallest necessary file edits
- no opportunistic improvements
```

Forbidden:

```text
- architecture redesign
- unrelated cleanup
- renaming unrelated logic
- modifying baselines without instruction
```

### MODE C — VALIDATION

Allowed:

```text
- tests
- diff analysis
- golden comparison
- export consistency checks
- release-readiness report
```

Forbidden:

```text
- feature changes
- UI improvements
- calculation modifications
```

---

## 7. VS Code / Codex Working Loop

Use this loop inside VS Code.

```text
1. Open VS Code at project root.
2. Run git status.
3. Confirm clean or document dirty files.
4. Create a small task branch.
5. Classify the change.
6. Give Codex ONE task only.
7. Run tests.
8. Manually inspect dashboard if UI affected.
9. Commit only the intended files.
10. Update changelog / handover.
11. Stop and create next tuple before continuing.
```

Recommended terminal sequence:

```bash
git status
git checkout feature/method-comparison-panel
git pull
python -m http.server 8000
npm test
```

Open locally:

```text
http://localhost:8000/index.html
http://localhost:8000/dashboard_modular.html
```

---

## 8. Standard Codex Prompt Block

Paste this before every implementation task.

```text
You are working on Cryogenic Material Dashboard v0.4.5.

MODE:
[THINKING | IMPLEMENTATION | VALIDATION]

CHANGE CLASS:
[E1 | E2 | E3 | V1 | V2 | X1 | T1 | D1 | R1 | A1]

STRICT RULES:
1. Preserve the existing engineering baseline.
2. Do not redesign the app.
3. Do not change calculation logic unless explicitly requested.
4. Do not mix UI changes with numerical-method changes.
5. Do not rename public functions unless required.
6. Do not touch excluded/archive/generated files.
7. Modify only the files required for this task.
8. After editing, list every changed file and changed function.
9. Run or explain the required tests.
10. Stop if the baseline or expected outputs become unclear.

Current baseline:
- 10 NIST materials
- k(T) and cp(T)
- Trapezoid, Simpson, Romberg, Gauss-Legendre
- Single Method and Compare All
- Delta Summary
- CSV/JSON/PNG export

Task:
[ONE SMALL TASK ONLY]
```

---

## 9. Recursive Artefact Pipeline

Future automation should convert conversation tuples into governed implementation tasks.

Target pipeline:

```text
RAW TUPLES
    ↓
tuple_parser.py
    ↓
structured_requirements.json
    ↓
RTM_generator.py
    ↓
task_queue.yaml
    ↓
Codex iteration prompt
    ↓
implementation
    ↓
regression validation
    ↓
handover generation
    ↓
new recursive state
```

The tuple parser should extract:

```text
A. Engineering Logic
B. Calculation Method
C. Visual / UI Requirement
D. Export / File Requirement
E. User Control / Workflow Requirement
F. Validation Requirement
G. Release / Handover Requirement
```

---

## 10. Required Governance Artefacts

Add or maintain these artefacts over time.

```text
CHANGE_CLASSIFICATION.md
SESSION_CONTEXT.json
contracts/
golden_outputs/
tests/regression/
releases/
```

Suggested structure:

```text
contracts/
  numerics.contract.json
  materials.contract.json
  export.contract.json
  ui.contract.json

golden_outputs/
  SS304_4K_20K_trapezoid.csv
  SS304_4K_20K_simpson.csv
  OFHC_4K_300K_romberg.csv

tests/regression/
  compare_to_golden.js
  validate_integral_ranges.js
  validate_export_consistency.js
  validate_method_deltas.js

releases/
  v0.4.5/
    release_manifest.json
    regression_summary.md
    validated_outputs/
    clean_zip/
```

---

## 11. Build Contract Example

Example contract for `js/numerics.js`:

```json
{
  "module": "js/numerics.js",
  "authority_level": "LEVEL_2_RUNTIME_IMPLEMENTATION",
  "allowed_changes": [
    "new_method",
    "performance_improvement",
    "bugfix_with_regression_proof"
  ],
  "forbidden_changes": [
    "change_existing_integral_results_without_baseline_approval",
    "rename_public_methods_without_migration",
    "modify_material_coefficients",
    "change_export_schema"
  ],
  "requires": [
    "npm_test_pass",
    "golden_output_comparison",
    "method_delta_report"
  ]
}
```

---

## 12. Session Continuity Engine

Recommended `SESSION_CONTEXT.json`:

```json
{
  "current_version": "0.4.5",
  "baseline_commit": "95feba55199f995dd5a3739a1bc1e8f374bb4d82",
  "active_branch": "feature/method-comparison-panel",
  "locked_modules": [
    "js/numerics.js",
    "js/materials.js",
    "data/materials.json"
  ],
  "current_governance_method": "recursive_idempotent_codex_mcp",
  "next_iteration_focus": [
    "baseline verification",
    "golden outputs",
    "regression fixtures",
    "change classification",
    "build contracts"
  ],
  "known_limits": [
    "no iterative layered-wall interface solver in HTML dashboard",
    "no uncertainty propagation / Monte Carlo",
    "v0.4.5 modular requires HTTP server for ES modules"
  ],
  "absolute_rule": "Do not combine visual, equation, export, method, and refactor changes in one iteration."
}
```

---

## 13. Recommended Next Iterations

### Iteration A — Baseline Verification

```text
CHANGE CLASS: D1/T1
MODE: VALIDATION
Goal: Confirm v0.4.5 runs cleanly before adding anything.
Output: BASELINE_VERIFICATION_v0.4.5.md
No app logic changes.
```

### Iteration B — Golden Outputs

```text
CHANGE CLASS: T1
MODE: VALIDATION
Goal: Create frozen reference outputs for selected materials/ranges/methods.
Output: golden_outputs/*.csv
No UI changes.
```

### Iteration C — Regression Engine

```text
CHANGE CLASS: T1
MODE: VALIDATION
Goal: Compare current outputs to golden outputs.
Output: tests/regression/compare_to_golden.js
No production logic changes unless test exposure is required.
```

### Iteration D — Build Contracts

```text
CHANGE CLASS: D1/A1
MODE: THINKING
Goal: Add machine-readable contracts for numerics, materials, export, and UI.
Output: contracts/*.contract.json
No runtime changes.
```

### Iteration E — cp/k Visual Clarity

```text
CHANGE CLASS: V1/V2
MODE: IMPLEMENTATION
Goal: Improve labels/tooltips to show whether active property is k(T) or cp(T).
No numerical method changes.
```

### Iteration F — v0.4.6 Release Candidate

```text
CHANGE CLASS: R1
MODE: VALIDATION
Goal: Version bump only after tests and baseline comparison pass.
Output: VERSION, CHANGELOG, FILE_INDEX, HANDOVER_v0.4.6.md
No app logic changes.
```

---

## 14. Git Discipline

Use one commit per logical iteration.

Preferred:

```bash
git status
npm test
git add <specific files only>
git commit -m "test: add v0.4.5 numerical regression fixtures"
```

Avoid:

```bash
git add .
```

Use explicit adds:

```bash
git add tests/regression/compare_to_golden.js golden_outputs/SS304_4K_20K_trapezoid.csv docs/CHANGELOG.md
```

---

## 15. MCP / Cloud Codex Handover Notes

If this repository is used by OpenAI Codex in the cloud or with MCP tools:

```text
- Read this file first.
- Read SESSION_CONTEXT.json second if present.
- Read CHANGE_CLASSIFICATION.md before proposing edits.
- Read contracts/*.json before modifying runtime modules.
- Treat golden_outputs/ as locked unless explicitly regenerating baselines.
- Do not infer engineering correctness from UI appearance.
- Do not alter method outputs without a regression report.
- Prefer documentation and task-queue generation before implementation.
```

Required MCP behaviour:

```text
1. Discover repo state.
2. Read source-of-truth docs.
3. Classify requested change.
4. Propose file-level plan.
5. Modify only authorized files.
6. Run or declare unavailable tests.
7. Produce changed-file summary.
8. Update recursive handover.
```

---

## 16. ABACUS Extension

Any `GBOGEB/ABACUS` workflow should use the same governance model.

ABACUS should be treated as the automation/orchestration layer for:

```text
- tuple parsing
- RTM generation
- task queue creation
- build contracts
- golden output management
- release manifest generation
- recursive handover production
```

ABACUS must not directly overwrite validated engineering logic without a change classification and regression proof.

---

## 17. Definition of Done

A recursive/idempotent Codex iteration is complete only when:

```text
- change class is declared
- execution mode is declared
- source-of-truth level is identified
- changed files are listed
- changed functions are listed where applicable
- tests are run or explicitly unavailable
- regression result is documented
- baseline impact is stated
- handover/session context is updated
- next recommended task is explicit
```

---

## 18. Final Operating Principle

```text
Do not optimize for speed.
Optimize for repeatability, traceability, and engineering confidence.
```

This repository should evolve as:

```text
Engineering Dashboard
+
Recursive Development System
+
AI Governance Framework
+
RTM / Traceability Engine
+
Controlled Codex Orchestrator
```

Not as an uncontrolled dashboard prototype.
