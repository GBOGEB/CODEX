# Federation Runtime (W003)

This enclave stages ABACUS ↔ CODEX governed semantic federation runtime assets without mutating root topology.

## PR-007 implementation pack
- Governance schema: `schema/governance_header.schema.json`
- Governance parser: `engines/governance_parser.py`
- CI gate: `.github/workflows/governance-gate.yml`
- PR template: `.github/PULL_REQUEST_TEMPLATE.md`
- Traceability manifest: `governance/traceability_manifest.json`
- Execution checklist: `docs/pr_007_execution_checklist.md`
- PR stream order: `governance/pr_track.yml`

## Local validation
```bash
python federation_runtime/engines/governance_parser.py \
  --target federation_runtime/.github/W003_PR_FOLLOW_UP.md \
  --schema federation_runtime/schema/governance_header.schema.json
```


## Handover lineage
- Full PR trace: `docs/FULL_PR_TRACE.md`
- Wave recreation plan: `governance/wave_recreation_plan.yml`
- Execution handover brief: `.github/EXECUTION_HANDOVER.md`
