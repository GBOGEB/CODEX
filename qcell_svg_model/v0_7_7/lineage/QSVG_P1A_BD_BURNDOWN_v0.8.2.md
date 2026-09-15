# QSVG-P1A BD burn-down — v0.8.2

## Pulse outcome

The deliberately narrow P1A frontier has now produced a canonical MAIN implementation from one SSOT and carried forward the strongest lessons from the user-edited sheet progression.

### C1 — MAIN_CONVERGENCE

- `QSVG-BD-001 canonical MAIN not consolidated` → **IMPLEMENTED_PENDING_VISUAL_ACCEPTANCE**
- `QSVG-BD-002 large-arrow policy not enforced` → **CLOSED_IMPLEMENTATION**

Evidence:
- one SSOT YAML;
- one canonical SVG;
- one interactive HTML;
- compact right-side A/B/D/E stream legend;
- dotted endpoint guides ON by default;
- big teaching arrows OFF by default;
- pressure overlay absent/OFF;
- temperature colour bar retained as authoritative heat-map mapping.

C1 can be treated as **CLOSE_CANDIDATE**, pending user/Codex visual review rather than further architecture invention.

### C2 — VISUAL_CONTROL

- `QSVG-BD-003 text collision` → **PARTIAL_STATIC_PASS_AUTOMATION_PENDING**
- `QSVG-BD-004 layer state` → **PARTIAL_TOGGLE_ENGINE_IMPLEMENTED**

The HTML now renders three controlled states from the same drawing:
1. thermal only;
2. thermal + parasitics;
3. full MAIN.

Remaining C2 work is automated bounding-box/collision checking and persisted layer state if still useful.

### C3 — PROOF_AND_REPEAT

- `QSVG-BD-005 deterministic regeneration` → **OPEN**
- `QSVG-BD-008 typed visual receipt` → **IMPLEMENTED_DRAFT**
- `QSVG-BD-009 distinct-SHA repeat` → **CLOSED_PASS_STABLE_ARTIFACT_REPEAT**

Distinct-SHA repeat proved the canonical SSOT/SVG/HTML blobs remained unchanged across two different branch heads. This is stability evidence only; it does not fabricate YAML→SVG generator determinism.

### C4 — DEFERRED_EXPANSION

- `QSVG-BD-006 pressure overlay` → **DEFERRED_NONBLOCKING**
- `QSVG-BD-007 hosted HTML` → **DEFERRED_NONBLOCKING**

### CONTROL

`QSVG-BD-010` remains **WITHHELD**.

## Contraction after P1A

Core open work is now effectively:

1. **C2 visual control** — automated collision + optional state persistence;
2. **C3 regeneration proof** — clean SSOT→SVG→HTML execution and normalized equality.

Pressure and hosting remain outside the current critical path.

## Recommended next pulse

`QSVG-P1B — collision and layer-state control`

Do not redesign MAIN in P1B unless a concrete review finding requires it.
