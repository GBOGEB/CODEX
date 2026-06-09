# Runtime Module Decomposition

## Core Modules

| Module | Purpose |
|---|---|
| renderer | HTML/dashboard rendering |
| topology | recursive graph traversal |
| validation | integrity verification |
| deployment | Pages/CI deployment |
| telemetry | runtime observability |
| debug_spine | Governed Debug Adapter Protocol sessions with Swift backbone and federated Python/JavaScript/TypeScript targets |

---

## Planned Extractions

### CODEX Retains

- engineering content
- technical dashboards
- domain manifests
- QPLANT-specific topology

### ABACUS Extracts

- runtime infrastructure
- CI primitives
- renderer engine
- validation engine
- telemetry framework
- debug spine governance contracts

---

## Future Federation

```text
CODEX ↔ Codex_Abac ↔ ABACUS
```

Enables:

- recursive orchestration
- multi-repo topology
- federated runtime governance
- portable engineering infrastructure
