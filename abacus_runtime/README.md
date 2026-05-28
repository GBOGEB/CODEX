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
