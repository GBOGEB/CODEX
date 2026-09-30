# MissionControl Mycelium Control Surface v0.2

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


## User abstract task instruction — developed concept

Treat MissionControl as a persistent **mycelium execution network**, not a chat transcript.

A user instruction is converted into a governed graph mutation:

```text
intent
  ↓
authority freeze
  ↓
current node + exact next edge
  ↓
dependency / precedence graph
  ↓
reverse-pressure ranking
  ↓
bounded execution
  ↓
proof edge
  ↓
outward projection
  ↓
temporal lineage + restart pointer
```

The visual stream is an observation and steering surface. Losing that stream must not reset the execution graph. A user steer is appended as a priority event and may change the active edge, but it does not erase completed proof, silently rebase history, or reintroduce cleared work.

### Layout contract

The same six semantic panels support multiple presentation geometries:

- **2 x 3** — canonical control-room layout;
- **3 x 2** — wide-screen layout;
- **golden focus** — one panel receives approximately 1.618× the adjacent width while the remaining panels stay available;
- **single focus** — one panel fills the review surface for small screens or detailed inspection.

The content model is independent of screen size. Unused space may remain as light/dark whitespace rather than stretching a panel until its information density becomes misleading.

### Current / mid / long horizon

Every active view should expose three horizons:

- **current** — exact node, first red, active action, evidence state;
- **mid** — admitted successors, dependency pressure, likely unblocks;
- **long** — governed objectives, release/DoV conditions, external-return dependencies.

Steering changes priority across these horizons while preserving lineage.

### Atoms, nodes, edges and graphs

Atoms are the smallest typed units that should be independently traceable. Nodes aggregate atoms into work, evidence, decisions, repositories or outward products. Edges carry semantics such as dependency, precedence, proof, block, publication, federation or supersession. Graphs are materialized views over those typed elements; they must never become a second source of truth.

### Outward-first navigation

MissionControl should continuously expose human-facing results: HTML, tables, plots, SVG/diagrams, PDF/DOCX/PPTX/XLSX when governed, and the source/original renderer or repository item that generated them. Plotly and Matplotlib may remain separate renderer families, but each visible result must retain the source path/revision that produced it.

### Federation choice

Prefer the least destructive integration mechanism that satisfies the work:

```text
bridge → cherry-pick → federation → exact pin → full merge
```

Full merge is not a maturity level; it is only appropriate when authority and ownership intentionally converge.
