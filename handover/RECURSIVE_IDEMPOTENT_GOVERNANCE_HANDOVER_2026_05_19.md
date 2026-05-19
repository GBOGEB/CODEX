# Recursive Idempotent Governance Handover

## Purpose

This handover consolidates the latest tuple outputs and establishes the canonical governance direction for GBOGEB/CODEX and downstream ABACUS integration.

This is a governance + orchestration update only.
No numerical baseline changes are permitted.

## Locked Baseline

Current protected engineering baseline:

```text
Branch: feature/method-comparison-panel
Version: v0.4.5
Commit: 95feba55199f995dd5a3739a1bc1e8f374bb4d82
```

Principles:

- Preserve engineering meaning.
- Preserve deterministic outputs.
- Separate UI from numerical methods.
- Prevent uncontrolled recursive drift.
- Maintain regression-oriented development.

## Required Governance Layers

### 1. Source of Truth Hierarchy

```text
LEVEL 0 — Immutable references
LEVEL 1 — Locked engineering baseline
LEVEL 2 — Runtime implementation
LEVEL 3 — Visual/UI layer
LEVEL 4 — Experimental
```

Rule:

```text
Experimental logic may never overwrite validated engineering baselines.
UI layers may never redefine engineering semantics.
```

---

### 2. Formal Change Classification

Required file:

```text
CHANGE_CLASSIFICATION.md
```

Required classifications:

| Type | Meaning |
|------|---------|
| E1 | Engineering calculation |
| E2 | Numerical method |
| E3 | Material property source |
| V1 | Visual only |
| V2 | UX only |
| X1 | Export only |
| T1 | Test only |
| D1 | Documentation only |

Mandatory rules:

- E-type changes require regression validation.
- V-type changes may not alter numerical outputs.
- T-type changes may not alter production logic.

---

### 3. Recursive Artefact Pipeline

Target architecture:

```text
RAW TUPLES
 -> tuple_parser.py
 -> structured_requirements.json
 -> RTM_generator.py
 -> task_queue.yaml
 -> Codex iteration prompt
 -> implementation
 -> regression validation
 -> handover generation
 -> recursive state update
```

---

### 4. Golden Outputs

Required:

```text
/golden_outputs/
```

Purpose:

- deterministic regression anchors
- protected numerical references
- release validation

---

### 5. Regression Engine

Required:

```text
tests/regression/
```

Suggested:

```text
compare_to_golden.js
validate_integral_ranges.js
validate_export_consistency.js
validate_method_deltas.js
```

---

### 6. Build Contracts

Required:

```text
/contracts/
```

Purpose:

- define allowed modifications
- define forbidden changes
- enforce validation requirements
- stop vibe-driven refactors

---

### 7. Codex Execution Modes

#### MODE A — THINKING

Allowed:

- analysis
- RTM extraction
- documentation
- comparison
- governance

Forbidden:

- code modification

#### MODE B — IMPLEMENTATION

Allowed:

- single scoped task

Forbidden:

- uncontrolled refactor
- architectural redesign
- unrelated renaming

#### MODE C — VALIDATION

Allowed:

- regression testing
- comparison
- diff analysis

Forbidden:

- feature additions

---

### 8. Release Governance

Required:

```text
/releases/
```

Structure:

```text
release_manifest.json
regression_summary.md
validated_outputs/
clean_zip/
```

---

### 9. Session Continuity Engine

Required:

```text
SESSION_CONTEXT.json
```

Purpose:

- preserve recursive state
- preserve locked modules
- preserve active branch context
- preserve unresolved engineering limits
- support MCP/cloud Codex continuation

---

## Core Rule

NEVER combine:

- numerical changes
- UI redesign
- export modifications
- architecture refactors
- semantic reinterpretation

inside one uncontrolled iteration.

## ABACUS Relationship

ABACUS is considered a compatible downstream orchestration and engineering runtime.

CODEX governance patterns should remain portable into:

- ABACUS_RENDER_PIPELINE
- tupleized orchestration
- YAML SSOT pipelines
- renderer governance
- RTM traceability engines
- semantic lineage systems

## Handover State

This handover is considered:

```text
PRIMARY GOVERNANCE SEED
```

for future:

- Codex cloud MCP continuation
- recursive tuple execution
- deterministic engineering governance
- multi-agent orchestration
- replayable engineering cognition
