# cADR — CODEX repository architecture

**ID:** TRIAGE-CADR-CODEX-001  
**Decision:** `GBOGEB/CODEX` is the TRIAGE KEB semantic/provenance governance parent.

## QPS authority source
The child authority for QPS engineering ADR/OCD content is `GBOGEB/cryoplant-project`, registered in:

`ocd-adr/20_canonical/control/QPS_GLOBAL_ADR_OCD_SSOT_v1.json`

This cADR is authoritative for CODEX repo-local semantic/provenance governance only. It is not an engineering ADR for QPS and cannot promote QPS facts, compliance, OCD content or engineering decisions.

## Decision
CODEX owns semantic normalization, provenance validation, schema governance, exact-hash gates, federation policy, CI truth verification and MCP governance runtime. It does not own QPS engineering truth, DOW scientific analysis or final child disposition.

## Canonical flow
```text
incoming governed child payload
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
2. KEB may append validation/normalization receipts but not rewrite or promote child QPS truth.
3. Semantic and provenance status are separate gates.
4. CODEX repo-local cADR/xOCD authority is scoped to CODEX governance/runtime and never supersedes child QPS ADR/OCD authority.
5. Historical or documentation-only bridge assets do not count as live federation penetration.
6. Generated Office/HTML/PDF artifacts are release children, not governing SSOT.
