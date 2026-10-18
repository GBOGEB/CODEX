# CODE PURPLE W1 — Swift/LLDB source roof and MIP native TestFlight

**Status:** additive CODEX-owned read-only census and testflight; no new engineering SSOT, executor, KEB acceptance, or governed merge authority. `MERGE_ADMISSION=HOLD`.

## Existing owners remain independent

| Ownership | Canonical path | Role |
|---|---|---|
| CODEX KEB | `scripts/lldb_dap_runtime_probe.py`; `.github/workflows/lldb-dap-swift-docker-runner-mcp.yml` | Producer of Swift LLDB runtime receipts |
| CODEX debug spine | `abacus_runtime/debug_spine/` | Swift session and DAP trace contract |
| ABACUS DOW / LDAB | `scripts/bd_ldab_join_census.py`, `tools/everred_v3/src/ldab_adapter.py` | Diagnostic evidence, not child acceptance |
| QPS TRIAGE | `triage/runtime_health/qps_lldb_probe.py`, `debug_pulse.py`, `qps-debug-dag.yml` | QPS-owned native proof and child disposition |
| Mission Control | `mission-control/v2/spine_w4` | Read-only graph and orchestration observation |

## Complete scoped Swift census

At inspected CODEX main SHA `f7fe32401e49455b381205cf050c52ad8ee6f472`, exactly four tracked CODEX Swift/SwiftPM files were found: `abacus_runtime/debug_spine/swift/Package.swift`, `abacus_runtime/debug_spine/swift/Sources/AbacusDebugSpine/main.swift`, `runtime/debug/federation/qps_payload/Probe.swift`, and `runtime/debug/lldb_dap_probe/Probe.swift`.

One external QPS file was observed at its own frozen SHA `c07666b2dfc77f97980e8661fac3864f975e2d76`: `triage/runtime_health/lldb_probe/Probe.swift`. Its external source is deliberately **DECLARED_NOT_CURRENT_READBACK** at execution time; this producer must not claim live federated completeness. The CODEX-local census fails closed on unregistered Swift files, including new sources introduced on the PR head.

## MIP / triple-pulse strategy

| Pulse | MIP | Native obligation | Remaining boundary |
|---|---|---|---|
| P1 | MODERNIZE | Enumerate source, track file hashes, execute positive + adversarial tests on exact head | Linux inventory is not native debugger proof |
| P2 | INNOVATE | macOS Swift compile + real LLDB breakpoint + at least two actual `stop reason = step over` events + backtrace, matched receipt SHA | LLDB CLI proof is not full DAP/MCP/Docker proof |
| P3 | PERPETUATE | CODEX KEB → ABACUS LDAB/DOW → QPS child disposition, repeat N-1 / N / N+1 native receipts | Owner-gated, not automated or accepted by this PR |

The previous probe counted echoed `thread step-over` commands plus repeated stop/backtrace text as one blended `steps` measure. That can inflate the measurement without additional actual stepping. The repaired producer now counts observed step-stop outcomes specifically, and requires a genuine breakpoint and backtrace. The W1 verifier tests falsified/hashed/stale/inflated native receipts and keeps `lldb_dap_live`, `docker_native`, `mcp_native`, QPS current acceptance and merge admission unproven.

## Run locally

```sh
python -m unittest discover -s tests/runtime -p test_swift_roof_mip.py -v
python scripts/swift_roof_mip.py --mode census --expected-head "$(git rev-parse HEAD)" --out /tmp/swift-roof
```

The exact-head macOS action is `.github/workflows/swift-roof-mip-testflight.yml`. It creates separate P1/P2 artifacts. It does not modify the existing CODEX or QPS dispatch/run triggers.

Historical CODEX workflow run `34508749625` has two successful jobs and artifacts, including a real macOS LLDB execution log. That observation is historical, not a verdict on manually triggered run #10 or on this new PR head. Missing job IDs, source freshness, review, or branch protection are UNKNOWN/HOLD, never PASS. No bypass, remote dispatch or engineering-credit promotion is allowed.
