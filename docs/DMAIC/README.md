# DMAIC — Quick-Start, Navigation & Federation Bridge

> **Status: BRIDGE**
> This directory is a quick-start guide, navigation layer, and federation bridge.
> It does **not** duplicate DMAIC lifecycle definitions.
> The canonical DMAIC definition lives in `99_handover/PROCESS_DMAIC.md`.

## Canonical Source

| Source | Description |
|--------|-------------|
| [`99_handover/PROCESS_DMAIC.md`](../../99_handover/PROCESS_DMAIC.md) | Authoritative DMAIC lifecycle definition |

## Quick-Start

| Phase   | Purpose                              | Key Output             |
|---------|--------------------------------------|------------------------|
| Define  | Scope the problem and goals          | Project charter        |
| Measure | Baseline current performance         | Process capability data |
| Analyze | Identify root causes                 | Root cause analysis    |
| Improve | Implement and validate solutions     | Improvement plan       |
| Control | Sustain the gains                    | Control plan           |

For full phase definitions, process gates, and lifecycle governance, refer to:
[`99_handover/PROCESS_DMAIC.md`](../../99_handover/PROCESS_DMAIC.md)

## Federation Bridge

This layer bridges DMAIC activity tracked across:

- [`docs/wave_packages/runtime/dmaic_telemetry_stats.py`](../wave_packages/runtime/dmaic_telemetry_stats.py) — telemetry
- [`docs/incubator-dmaic-dashboard.html`](../incubator-dmaic-dashboard.html) — dashboard
- [`docs/rtm/incubator_rtm_bridge.md`](../rtm/incubator_rtm_bridge.md) — RTM phase map

## Navigation

```
Canonical DMAIC lifecycle  →  99_handover/PROCESS_DMAIC.md
DMAIC telemetry            →  docs/wave_packages/runtime/dmaic_telemetry_stats.py
DMAIC dashboard            →  docs/incubator-dmaic-dashboard.html
Phase → RTM traceability   →  docs/rtm/incubator_rtm_bridge.md
```

> **Reconciliation Note:** Overlap with `99_handover/PROCESS_DMAIC.md` measured at 74%.
> This layer was converted from an authoritative source to a quick-start / federation bridge
> as part of PR-000A Governance Bootstrap Reconciliation.
