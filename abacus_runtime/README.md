# ABACUS Runtime Extraction

## Purpose

Extract reusable runtime infrastructure from CODEX into ABACUS-compatible modular components.

## Target Components

- Pages deployment engine
- runtime renderer
- topology validator
- manifest orchestrator
- dashboard generator
- CI runtime primitives

## Strategic Direction

```text
CODEX
  ↓ domain content
ABACUS
  ↓ reusable runtime infrastructure
Codex_Abac
  ↓ orchestration federation
```

## Runtime Goals

- infrastructure portability
- reusable CI/CD
- recursive orchestration
- multi-repository federation
- runtime abstraction

## Bridge Utility

Generate an export bundle plus a machine-readable bridge report with:

```bash
python scripts/export_abacus_runtime.py --report-json outputs/runtime_export/bridge_report.json
```

## Governance Boundary

ABACUS runtime components own ingestion and engine execution concerns, including manifest processing, SSOT generation, source indexing, RTM extraction, document processing, dashboard generation, and runtime validation. Governance authority remains routed through `GOVERNANCE.md`, `docs/GOVERNANCE/`, `MANIFEST/`, `DELTA_1/`, and `KEB/governance/`; ABACUS references those sources without redefining their canon.
