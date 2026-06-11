# ABACUS_DEBUG_SPINE_W000

## Purpose

`ABACUS_DEBUG_SPINE_W000` scaffolds the first parallel runtime/debug governance track for the GBOGEB federation. It treats a debug session as a governed runtime artifact instead of an ephemeral developer action.

Root mantra:

```text
IF IT CANNOT TRACE, IT CANNOT DEBUG.
IF IT CANNOT DEBUG, IT CANNOT GOVERN.
IF IT CANNOT RENDER, IT CANNOT GOVERN.
```

## Track Identity

| Field | Value |
|---|---|
| Track | `ABACUS_DEBUG_SPINE_W000` |
| Branch | `wave/W000-debug-spine-lldb-dap-swift` |
| Control surface | `lldb-dap` |
| Native backbone | Swift debug/session runtime |
| Federated targets | Python, JavaScript, TypeScript |
| Evidence layer | ABACUS trace/render/evidence governance |
| Persistence substrate | GitHub issues, actions, artifacts, commits, pull requests |

## Governance Objective

The W000 debug spine establishes the minimum control-plane contract required before implementation waves add live adapters or executable debug orchestration. The scaffold intentionally separates:

1. **Control** — `lldb-dap` owns Debug Adapter Protocol session control.
2. **Backbone** — Swift owns native session state, debug lifecycle, and DAP message normalization.
3. **Targets** — Python, JavaScript, and TypeScript are federated pipeline targets attached through runtime-specific launch profiles.
4. **Trace** — ABACUS emits durable session spans, breakpoints, launch state, evidence packets, and render inputs.
5. **Audit** — GitHub persists execution evidence through Actions logs, artifact bundles, issue links, PR lineage, and commit references.

## W000 Scope

W000 is a scaffold wave. It does **not** claim a production debugger implementation. It creates the canonical manifest, trace contract, and validation tests needed for follow-on implementation waves.

### In scope

- Debug governance manifest.
- Required runtime roles and target languages.
- Trace/render/evidence contract schema.
- Repository-level runtime registry linkage.
- Tests that prevent silent removal of W000 invariants.

### Out of scope

- Launching `lldb-dap`.
- Shipping Swift source packages.
- Debugging Python, JavaScript, or TypeScript programs.
- Uploading GitHub artifacts.

## Required Evidence Events

Every governed debug session must eventually emit these ABACUS events:

| Event | Purpose |
|---|---|
| `session.created` | Captures the GitHub, branch, commit, actor, and target runtime context. |
| `dap.initialized` | Proves `lldb-dap` negotiated the session control surface. |
| `breakpoint.bound` | Records source, line, adapter response, and runtime target binding. |
| `execution.paused` | Captures stack, thread, variable-scope, and stop reason evidence. |
| `render.snapshot` | Converts trace state into ABACUS renderable evidence. |
| `session.closed` | Finalizes result, artifact links, and governance disposition. |

## Follow-on Waves

- **W001** — Swift package skeleton and DAP message model.
- **W002** — `lldb-dap` launch/attach profile normalization.
- **W003** — Python/JavaScript/TypeScript federated target adapters.
- **W004** — GitHub Actions evidence upload and PR audit linkage.
- **W005** — ABACUS render dashboard for governed debug sessions.

## W001 Runtime Proof

W001 adds the first executable proof path while preserving the W000 governance folder and contract:

1. Build the Swift package:

   ```bash
   swift build --package-path abacus_runtime/debug_spine/swift
   ```

2. Emit a JSONL runtime trace:

   ```bash
   swift run --package-path abacus_runtime/debug_spine/swift abacus-debug-spine \
     --trace-output runtime/logs/abacus_debug_spine_w001_trace.jsonl \
     --target-language Python
   ```

3. Render the trace into Markdown evidence:

   ```bash
   python abacus_runtime/debug_spine/render_evidence.py \
     --trace-jsonl runtime/logs/abacus_debug_spine_w001_trace.jsonl \
     --output-md runtime/logs/abacus_debug_spine_w001_evidence.md
   ```

The versioned LLDB-DAP launch template lives at `lldb-dap/launch.template.json` and points to the Swift executable plus the expected JSONL and Markdown evidence paths.
