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
  --schema federation_runtime/schema/governance_header.schema.json \
  --traceability-manifest federation_runtime/governance/traceability_manifest.json \
  --pr-track federation_runtime/governance/pr_track.yml \
  --wave-plan federation_runtime/governance/wave_recreation_plan.yml
```

The parser logs governed input paths, validation process steps, and structured output
(`PR-ID`, `WAVE`, and stream coverage) to support drift detection and execution traceability.


## Handover lineage
- Full PR trace: `docs/FULL_PR_TRACE.md`
- Wave recreation plan: `governance/wave_recreation_plan.yml`
- Execution handover brief: `.github/EXECUTION_HANDOVER.md`

## Pipeline integration bridges
- Main-repo governance gate: `.github/workflows/w003-governance-gate.yml`
- Stack-level bridge validation: `.github/workflows/full-stack-governance.yml` (CODEX, ABACUS, MCP bridge components)
