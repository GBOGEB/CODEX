# MissionControl Mycelium Control Surface v0.1

## Goal

Create a durable, user-facing control plane in **GBOGEB/CODEX** that lets a human follow and steer a federated engineering/program workflow without turning UI disconnects, stream timeouts, or unrelated blocked lanes into global execution stops.

The metaphor is a **mycelium network**:

- **atoms** are the smallest governed work/evidence units;
- **nodes** are repos, issues, PRs, tests, requirements, decisions, artifacts and outputs;
- **edges** carry dependency, precedence, proof, federation and publication semantics;
- **graphs** expose the active system state;
- **reverse pressure** propagates blocked downstream value back to the predecessor that can actually unblock it;
- **lineage** keeps every visible state tied to exact evidence and authority.

## Six-view user surface

The canonical UI is a responsive **2 x 3** grid. Every panel is 16:9 and can be focused independently.

1. Repository topology
2. Interaction graph
3. Execution and recovery
4. Evidence and lineage
5. DMAIC / KPI / PCA / Bradley-Terry
6. Outward artifacts

On narrow screens the same six panels stack vertically. The page must preserve function and traceability at any size; whitespace is allowed rather than distorting the panels.

## Recovery rule

A presentation-stream timeout is **not** an execution failure.

The durable state is the repository checkpoint tuple:

```text
repo + branch + head SHA + current step + completed steps
+ blockers + evidence refs + next legal transition
```

A reconnect resumes from that tuple. Completed slices are not replayed merely to reconstruct chat/UI state.

Only the affected lane stops when its own first red is material. Independent lanes continue.

## Graph semantics

Every promoted state requires a proof edge. Remote engineering truth remains remote authority. CODEX owns presentation, orchestration, graph contracts and navigation; it does not silently promote ABACUS or cryoplant engineering state.

## Analytics

DMAIC is the lifecycle spine. KPI is the operational state. PCA is diagnostic and requires a governed population. Bradley-Terry is permitted only from observed pairwise outcomes; it must not be synthesized from subjective scores or PC ordering.

## Outward evidence

The control surface should expose or link:

- live/static HTML;
- GitHub repo, issue, PR, commit and workflow surfaces;
- PDFs, DOCX, PPTX, XLSX and images when governed outward artifacts exist;
- tables and diagrams;
- Plotly interactive analytics;
- Matplotlib static evidence;
- source/original artefacts for externally maintained visualizations.

## Federation rule

External repositories may be integrated by the least destructive mechanism that preserves authority and lineage:

```text
link/reference
→ bridge/adapter
→ item import
→ cherry-pick
→ bounded merge
→ full merge only when ownership and authority truly converge
```

The graph must record which mechanism was used and preserve source repo, source SHA, target repo, target SHA and proof.

## Definition of Done

See `mission_control/mycelium/control_manifest.yaml`. Visualization alone never creates engineering or formal credit.
