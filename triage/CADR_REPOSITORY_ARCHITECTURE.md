# cADR — CODEX repository architecture

**ID:** TRIAGE-CADR-CODEX-001  
**Decision:** `GBOGEB/CODEX` is the TRIAGE KEB semantic/provenance governance parent.

## Decision
CODEX owns semantic normalization, provenance validation, schema governance, exact-hash gates, federation policy, CI truth verification and MCP governance runtime. It does not own QPS engineering truth, DOW scientific analysis or final child disposition.

## Canonical flow
```text
incoming governed payload
        |
        v
schema -> semantic normalization -> provenance/hash gate
        |                              |
        +------------------------------+
                       |
                       v
                 typed KEB receipt
                       |
                 federation dispatch
                       |
                 normalized return
                       |
                 child re-entry
```

## Bridge boundary
`src/bridge_adapter.py` is an executable adapter surface; `scripts/bridge_orchestrator.py` validates/orchestrates bridge configuration. Documentation-only bridge plans are not counted as active runtime edges unless bound to executable code or CI.

## Invariants
1. Exact governed identity survives roundtrip.
2. KEB may append validation/normalization receipts but not rewrite child truth.
3. Semantic and provenance status are separate gates.
4. Historical or documentation-only bridge assets do not count as live federation penetration.
5. Generated Office/HTML/PDF artifacts are release children, not governing SSOT.