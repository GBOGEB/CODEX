# W110 MIP Canonical SSOT Registry

This registry exposes the shared SSOT boundary for the core QPS triage triad and
the smaller repos that were active in the last 24 hours.

## Previous tail fixed

The LLDB-DAP / Swift / Docker / runner / MCP tail is retained as historical
receipt-backed **ACCEPT** proof, not as current-head W110 proof.

- CODEX receipt PR: [#598](https://github.com/GBOGEB/CODEX/pull/598)
- CODEX exact head: `5e58badb150df9ce0423e1d02f9d913380d4597d`
- workflow run: [34508749625](https://github.com/GBOGEB/CODEX/actions/runs/34508749625)
- artifact digest:
  `sha256:1e66581b7e2c53db6526eb08490cf744554618025e52e7691ed74373de0ad150`
- receipt SHA256:
  `3b32650abf18b824b5f3f06a113139ce470900c0957cef9d44c4b4e6e920f2d1`
- real LLDB steps: `10`
- DOW follow-up: [ABACUS #1103](https://github.com/GBOGEB/ABACUS/pull/1103)
- child disposition: [cryoplant #842](https://github.com/GBOGEB/cryoplant-project/pull/842)

## Active smaller repos

| Repo | Observed SHA | Role | MIP level-1 state |
| --- | --- | --- | --- |
| GBOGEB/codespaces-jupyter | `98e18d6e80a7335b329bbcd39f651e8ba95de1e6` | JUPYTER_RUNTIME_PRODUCER | CANDIDATE_ACTIVE |
| GBOGEB/CODESPACES_jyperter | `eda6aa0f576e276a3dd335555ebcf7f740f7f1b2` | CODESPACE_RUNTIME_PROOF | ACTIVE_EXACT_HEAD_PROOF_REPORTED |
| GBOGEB/DOCX_RTM_Automation | `28cc8d97c751cff2bad44a5cbf83ebcf6379641d` | DOCX_RTM_AUTOMATION | ACTIVE_CI_REGISTRY_RECEIPT |
| GBOGEB/cryogenic-accelerator-workspace | `771b4b6f4e45722125aa65bd42f9052f3659f5bf` | BRIDGE_RUNTIME_PROOF | ACTIVE_P6_BRIDGE_PROOF |
| GBOGEB/cryo_leak_rate_dashboard | `6ef501f37bc9c41dc50c4c0b54095963b02630f6` | LEAK_EVIDENCE_RUNTIME_PROOF | ACTIVE_P5_LEAK_PROOF |

## MIP actions

- Modernize: separate historical receipts from current-head proof and expose stale
  SSOT gaps directly.
- Innovate: treat smaller active repos as satellite runtime/tooling producers
  around the KEB -> DOW -> child chain.
- Perpetuate: require exact-head receipts and repo-local visible SSOT pointers
  before satellite promotion.

## Zod

The executable contract is:

`federation/mip/W110_CANONICAL_SSOT_REGISTRY.zod.ts`

Current satellite disposition is **DEFER** until repo-local SSOT pointers exist.
