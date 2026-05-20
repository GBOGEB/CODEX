# Recursive Idempotent Engineering Methodology — Handover v1.0

## Purpose

This document consolidates the latest tuple-based recursive engineering workflow into a formalized CODEX/ABACUS-compatible execution model.

Primary objectives:

- deterministic generation
- recursive continuation
- DMAIC governance
- idempotent rebuilds
- Codex-controlled execution
- regression-safe engineering evolution
- PR-driven traceability

Derived from:
- FULL TUPLE SET.txt
- FULL conversation TUPLE (raw).txt
- 19_05_Recursive Idempotent Method.txt
- QUAD_BT recursive deck lineage

---

# Finalized Engineering Intent Tuple

```text
(History: Recursive_Input)
    -> (Engine: DMAIC_Logic)
    -> (Output: Parametric_Artifacts)
```

Expanded operational interpretation:

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

---

# Canonical Source Hierarchy

## LEVEL 0 — Immutable references

```text
NIST equations
Validated CSVs
BAS equations
Approved RTM clauses
```

## LEVEL 1 — Locked engineering baseline

```text
validated outputs
reference decks
golden regression fixtures
release manifests
```

## LEVEL 2 — Runtime implementation

```text
js/*.js
python/*.py
render engines
plot generators
export pipelines
```

## LEVEL 3 — Visual/UI layer

```text
style.css
themes
layout
annotations
slide grammar
```

## LEVEL 4 — Experimental

```text
ML
optimization
future hooks
Monte Carlo
prototype logic
```

---

# Mandatory Governance Files

## CHANGE_CLASSIFICATION.md

Required change classes:

| Type | Meaning |
|---|---|
| E1 | Engineering calculation |
| E2 | Numerical method |
| E3 | Material property source |
| V1 | Visual only |
| V2 | UX only |
| X1 | Export only |
| T1 | Test only |
| D1 | Documentation only |

## SESSION_CONTEXT.json

Persistent recursive memory state.

Example:

```json
{
  "current_version": "0.4.5",
  "baseline_commit": "95feba5",
  "locked_modules": [
    "numerics.js",
    "materials.json"
  ],
  "next_iteration_focus": [
    "regression fixtures"
  ]
}
```

## /golden_outputs/

Frozen engineering references.

## /contracts/

Machine-readable build contracts.

## /tests/regression/

Mandatory regression validation.

---

# Codex Execution Modes

## MODE A — THINKING

Allowed:

```text
analysis
comparison
documentation
RTM extraction
planning
```

Forbidden:

```text
code modification
```

## MODE B — IMPLEMENTATION

Allowed:

```text
single scoped tasks
```

Forbidden:

```text
architecture redesign
broad refactors
unrelated renaming
```

## MODE C — VALIDATION

Allowed:

```text
comparison
regression testing
diff analysis
```

Forbidden:

```text
feature additions
```

---

# Dashboard Evolution Requirements

The MTBF/lambda dashboard shall support:

- dual-axis logic
- adaptive axis scaling
- logarithmic handling near lambda → 0
- scenario presets
- validity-checked inputs
- campaign probability visualization
- architecture comparison
- failure-budget closure
- operational-state sequencing

Core equations:

```text
λ = 1 / MTBF
R(t) = exp(-λt)
R_system = ∏ R_i
R_parallel = 1 - ∏(1 - R_i)
```

---

# Visual Engineering Rules

The deck system shall:

- preserve engineering density
- avoid dilution
- maintain outward-facing visual quality
- support left/right engineering storytelling
- support equation slides
- support worked examples
- preserve architectural sequence logic
- preserve operational-state transitions

Preferred render structure:

```text
LEFT:
- engineering explanation
- equations
- rationale

RIGHT:
- figures
- architecture diagrams
- campaign plots
- state logic
```

---

# CODEX + ABACUS Integration Intent

CODEX:
- GitHub orchestration
- recursive state control
- PR governance
- artifact lineage
- release management

ABACUS:
- engineering runtime
- numerical logic
- dashboard execution
- traceability math layer

Shared principles:

- deterministic rebuilds
- no silent compression
- regression-safe evolution
- recursive handover continuity
- stop-gate validation

---

# PR Governance Requirements

Every PR shall include:

```text
- intent
- scope
- classification
- regression impact
- baseline comparison
- stop gates
- release notes
```

Forbidden:

```text
visual + equation + architecture + export changes in one iteration
```

---

# Final Architecture Statement

This system is NOT only a dashboard.

It is:

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

---

# Recommended Next Actions

1. Add CHANGE_CLASSIFICATION.md
2. Add SESSION_CONTEXT.json
3. Create regression engine
4. Create tuple_parser.py
5. Create structured_requirements.json schema
6. Add golden_outputs/
7. Add contracts/
8. Split CODEX vs ABACUS runtime ownership
9. Add release manifests
10. Add PR templates with stop-gate logic

---

# Status

Current status:

```text
OPERATIONAL FOUNDATION: STRONG
RECURSIVE GOVERNANCE: PARTIAL
ENGINEERING REGRESSION CONTROL: MISSING
SESSION CONTINUITY: PARTIAL
FULL CODEX ORCHESTRATION: IN PROGRESS
```

Target state:

```text
FULL RECURSIVE + IDEMPOTENT + GOVERNED ENGINEERING PLATFORM
```
