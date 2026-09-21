# HISTORIAN CODEX Debugger/MCP CONTROL Closure

Issue: #675  
Parent: `GBOGEB/pipeline-automation-hub#76`  
Reviewed CODEX main: `155e373a943141c6c376fa43d5af21825a6088eb`  
Disposition: `NO_ACTIVE_DEBUGGER_DEBT`  
Authority transfer: `false`

## Scope

This receipt closes the CODEX-local Historian walk for the debugger/MCP CONTROL fabric. It does not close the independent cryoplant repository-local runner gate and does not create engineering, negotiation, or project DoV credit.

## Reconstructed lineage

| Slice | PR / merge | Executed evidence | Current classification |
|---|---|---|---|
| Exact QPS LLDB payload | #655 -> `942c784...` | macOS compile/LLDB real steps, exact payload binding | IMPLEMENTED_SURVIVES |
| Xcode lldb-dap resolution | #656 -> `141e7a9...` | adapter path/readiness bound into receipt | IMPLEMENTED_SURVIVES |
| KEB exact-payload binding | #658 -> `e34c9b5...` | federated receipt retains repo-local gate as WITHHELD_EXTERNAL | IMPLEMENTED_SURVIVES |
| Direct runtime -> KEB | #659 -> `7b26bba...` | one-job execution + KEB artifact | IMPLEMENTED_SURVIVES |
| Multi-adapter runtime fabric | #663 -> `f2fa2c0...` | lldb-dap/debugpy/js-debug/Docker/MCP/heartbeat lanes established | IMPLEMENTED_SURVIVES |
| js-debug + Docker first-red repair | #664 -> `2ddee91...` | Docker runtime LLDB PASS; js-debug repair path | SUPERSEDED_WITH_REPLACEMENT by #665/#666 |
| js-debug canonical launch | #665 -> `86892dd...` | exact-head run `34714638372` exposed remaining js-debug stall | SUPERSEDED_WITH_REPLACEMENT by #666 |
| js-debug diagnostic/control convergence | #666 -> `bd772ae...` | run `34718779772`: debugpy ACCEPT, js-debug ACCEPT, lldb-dap ACCEPT, Docker ACCEPT, heartbeat 3/3, federated CONTROL | IMPLEMENTED_SURVIVES |
| Official lldb-mcp materialisation | #667 -> `a28994f...` | run `34719383470`: official 23.1 toolchain live; strict managed-session assumption rejected | SUPERSEDED_WITH_REPLACEMENT by #668/#669 |
| Version-bound release MCP contract | #668 -> `2b24f30...` | release 23.1 two-tool contract separated from managed-session contract | IMPLEMENTED_SURVIVES |
| Strict four-tool dev contract | #669 -> `034b5ed...` | official development toolchain strict proof lane | IMPLEMENTED_SURVIVES |
| Main perpetuation | #670 -> `5d26e30...` | exact head `28684e8...`: QPS LLDB MCP Strict DoV run `34730500375` SUCCESS; MCP consumer run `34730500283` SUCCESS | IMPLEMENTED_SURVIVES |
| Review-debt repair | #676 -> `84c7fa3...` | exact head `dceb67f...`: QPS Perpetual Debug Control run `34774690027` SUCCESS; MCP consumer run `34774689923` SUCCESS | IMPLEMENTED_SURVIVES |

## Review finding classification

Historical review of #668 produced four relevant findings:

1. executable/shebang state -> `IMPLEMENTED_SURVIVES`;
2. generic subprocess/untrusted-input scanner warning -> `INVALIDATED` for this path because the binary is internally resolved and shell execution is not used;
3. broad outer exception -> `INVALIDATED_AS_BD / ACCEPTED_DESIGN` because it converts probe failure into a structured fail-closed receipt;
4. removable Python `assert` on live MCP stdio pipes -> `STILL_BD` at discovery, repaired by #676.

Current `scripts/qps_lldb_mcp_probe.py` contains an explicit stdio-pipe branch that terminates/kills safely and emits `REJECT / WITHHELD` with `bd_id=HIST-BD-014`; the removable runtime invariant no longer exists.

## Recurrence and survival

- review finding count: 4
- concrete CODEX-local STILL_BD findings: 1
- repaired: 1
- repair survival on reviewed main: PASS
- recurrence root: `runtime_fail_closed_stdio_invariant`
- recurrence after #676: 0 observed
- open CODEX-local debugger BD: 0

The remaining `BD03-EXT-RUNNER-001` is not CODEX implementation debt. It is the separately governed cryoplant repository-local runner/admission requirement and remains `WITHHELD_EXTERNAL`.

## CONTROL boundary

Current CODEX debugger/MCP fabric retains:

- real lldb-dap execution;
- real debugpy DAP execution;
- real vscode-js-debug execution;
- real Docker remote LLDB execution;
- official LLVM lldb-mcp release and strict managed-session profiles;
- heartbeat/control aggregation;
- KEB provenance binding;
- fail-closed MCP pipe handling.

No historical feature is reopened merely because it appeared in an earlier PR.

## Historian return

```yaml
reviewed_main_sha: 155e373a943141c6c376fa43d5af21825a6088eb
review_finding_count: 4
open_bd: 0
repair_survival: PASS
post_merge_survival: PASS
current_control_regressions: 0
external_withheld:
  - BD03-EXT-RUNNER-001
next_action: NO_ACTIVE_DEBUGGER_DEBT
authority_transfer: false
```

Re-entry is permitted only if a new current-code defect, missed review debt, heartbeat regression, provenance gap, or measured H4 pressure is observed.
