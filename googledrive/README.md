# CODEX Agentic Drive Reconciliation Bridge

Provisional ingestion layer supporting static offline blueprint analysis and agentic routing via Gemini 3.1 Pro.

### Execution Protocols
* **Offline Baseline Checks:** `./googledrive/scripts/run_reconciliation.ps1`
* **Agentic Sync Routing:** `./googledrive/scripts/run_sync.ps1`

All code evaluation is review-first; production target files are never modified dynamically without human verification.

## File Matrix

```text
googledrive/
  .codex-exchange.yaml
  README.md
  decision_log.jsonl
  inbound_staging/
    .gitkeep
  scripts/
    reconcile_drive.py
    drive_sync_agent.py
    run_reconciliation.ps1
    run_sync.ps1
```

## Safety Notes

* `decision_log.jsonl` is an append-only local audit ledger for proposed routing decisions.
* `inbound_staging/` is a local drop zone; raw staged artifacts are ignored by git except for `.gitkeep`.
* Notebook outputs and execution counts are scrubbed before agentic evaluation.
* Allowed routing strategies are `PRUNE`, `BRIDGE`, `CHERRY-PICK`, `PARALLEL`, and `DISCARD`.
* Target paths are validated as repository-relative paths with no parent traversal.
* API keys must be supplied through the process environment and must not be committed.

## Compatibility Shims

The root-level `scripts/drive_sync_agent.py` and `scripts/run_sync.ps1` entrypoints are intentional compatibility shims. They preserve the earlier invocation paths while delegating to the canonical implementations under `googledrive/scripts/`; the bridge logic remains centralized in the `googledrive/` package.

