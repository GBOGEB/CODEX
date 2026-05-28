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
- Bridge audit script: `scripts/check_federation_governance.py` (run locally or in CI to see real vs scaffold status)

## Real code vs scaffold inventory
| Path | Status | Notes |
|---|---|---|
| `federation_runtime/engines/governance_parser.py` | **Real** | Executable governance header validator |
| `federation_runtime/schema/governance_header.schema.json` | **Real** | JSON schema with `additionalProperties:false` |
| `federation_runtime/governance/traceability_manifest.json` | **Real** | W003 machine-readable traceability manifest |
| `tests/test_governance_parser.py` | **Real** | Pytest coverage for parser enforcement cases (9 tests) |
| `.github/workflows/w003-governance-gate.yml` | **Real** | Root CI workflow, discovered by GitHub Actions |
| `.github/workflows/full-stack-governance.yml` | **Real** | CODEX/ABACUS/bridge stack CI with federation bridge build |
| `bridge_manifest.yaml` | **Real** | CODEX↔ABACUS bridge topology declaration |
| `abacus_render_pipeline/A6_renderer_governance/TUPLE_OFFLOAD/tuple_offload_executor.py` | **Real** | Executable tuple offload and semantic state externalization |
| `output/federation_bridge/` | **Deprecated** | Canonical path is `outputs/html/federation_bridge/` (generated in CI via `federation_bridge_cli.py`) |

Run `python scripts/check_federation_governance.py` for a live status report.

## Tuple offload executor

The tuple offload executor processes conversation tuples and externalizes semantic state:

```bash
# Validate input only
python abacus_render_pipeline/A6_renderer_governance/TUPLE_OFFLOAD/tuple_offload_executor.py --validate-only

# Generate tuple manifest and summary
python abacus_render_pipeline/A6_renderer_governance/TUPLE_OFFLOAD/tuple_offload_executor.py
```

Output artifacts:
- `outputs/tuple_offload/tuple_manifest.json` - Full tuple manifest with lineage
- `outputs/tuple_offload/tuple_summary.md` - Human-readable summary with maturity assessment
