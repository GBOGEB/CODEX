# MissionControl Mycelium Control Surface v0.2.1

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

1. **Command / Input Root** — text, JSON/YAML-like input, local config upload, Dry Run / staged Apply, manual steering and source-authority context.
2. **Execution / Recovery** — active lanes, current atom, checkpoint, blocker, retry/resume intent and next legal transitions.
3. **Mycelium Graph** — graph navigation plus authority, evidence, critical-path and reverse-pressure overlays.
4. **Output / Evidence** — graph-driven artifacts, manifests, hashes/SHAs, evidence and provenance deeplinks.
5. **Analytics** — DMAIC / KPI / PCA / Bradley-Terry / density with non-authoritative guards.
6. **Federation Control** — repo heads, bridge/reference state, source→target lineage, cherry-pick/merge/conflict state and preserved remote authority.

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

## THIS IS THE WAY — one graph, multiple projections

**ENGINEERING VIEW and CONTROL VIEW are two projections of the same graph.**

The canonical control example is deliberately preserved as a first-class invariant:

```text
ENGINEERING VIEW
Cryoplant
→ 2 K refrigeration
→ B interface
→ pressure drop
→ calculation

CONTROL VIEW
P0
→ CRYO-IF-B unresolved
→ DOW calculation missing
→ blocks ICD freeze
→ blocks offer disposition
```

These are not duplicate records. The projection selector changes visibility and emphasis only. Node identity, evidence lineage, authority, maturity and history remain common.

### Observability projection

A third projection measures the same nodes:

```text
same node
├─ maturity
├─ QA
├─ code health
├─ debug / first-red recurrence
├─ docking / federation health
├─ ports / interface-probe health
├─ logs / log-analysis health
├─ reverse-pressure BD load
├─ DMAIC phase
├─ PCA diagnostic position
└─ Bradley–Terry rank (only from observed pairwise outcomes)
```

Every score must be tagged `MEASURED`, `DERIVED_FROM_MEASURED`, or `WITHHELD`. Missing inputs are shown as missing; they are not imputed merely to make a dashboard complete.


## v0.2.1 durable reentry

The control-plane reentry authority is `mission_control/mycelium/reentry_v0_2.yaml`.
Its browser-safe projection is `docs/data/missioncontrol_control_plane.json`.
The universal graph may contain cycles, while `executable_projection.json` must remain a DAG.

The preserved predecessor proof chain is repository-native:

```text
PR #839 exact head
→ >0-step MissionControl hosted execution
→ validator + tests + deterministic materialization GREEN
→ merge/readback
→ GitHub Pages build/deploy GREEN
→ MYCELIUM_V02_PR839_PROOF.json
→ v0.2.1 continuation
```

The static Pages surface is a control and steering surface, not an authenticated mutation gateway. **Apply request** stages a typed envelope and remains withheld until an authenticated executor binds repository/runtime proof.

Temporal continuation uses append-only `control_events.json` plus **current / mid / long** priority horizons. A user steer appends intent and changes priority; it never replays completed atoms solely to reconstruct conversation state.


## Authenticated execution gateway v0.1

Static GitHub Pages remains credential-free and cannot mutate repositories.
An APPLY request now stages a typed envelope, live-probes the public CODEX
`main` head for an exact source lock, and links to the GitHub-authenticated
workflow surface:

`MissionControl Authenticated Command Gateway`

Gateway v0.1 is deliberately narrow:

- authentication: GitHub authenticated actor with workflow-dispatch permission;
- authorization: exact source SHA + fixed repository/lane + action allow-list;
- enabled action: `REFRESH_FEDERATION_HEADS` only;
- mutation: automation branch + pull request only;
- direct write to `main`: forbidden;
- remote engineering/execution authority: preserved;
- receipt: actor, run, source SHA, envelope digest, action and changed paths;
- runtime proof: withheld until a real owner-dispatched gateway dry run executes.

Artifact cards also derive provenance from the same interaction graph, exposing
typed incoming/outgoing edges plus available source/target SHA, mechanism and
proof metadata. This is a view over the governed graph, not a second source of
truth.
