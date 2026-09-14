# CODEX / GEMINI Federation Runtime — Next-Wave Planning Candidate

**Status:** historical design candidate; not implementation evidence.  
**Raw provenance:** `Pasted text(15).txt`  
**Raw SHA256:** `39375c537b67a4f42f47bf7310bae0234f1d2cf4469d7418e9821cf4997781da`

## Context

This capture contains a planning thread for CODEX/GEMINI federation-runtime evolution. The recurring decision is **`TEMPLATE_DUPLICATION_WITH_DELTA`**: preserve the prior wave as a reusable governance template and change only the wave-specific scope, evidence targets, repo identity, CI findings, portal outputs and acceptance criteria.

The text is primarily architecture/planning material. It must not be read as proof that the proposed workflows, repository structures or controls were implemented.

## Core planning decision

The proposed integration ladder is:

1. **Identity & readiness** — verify repo purpose, boundaries, claimed-vs-actual state and evidence readiness.
2. **Loose merge / SSOT alignment** — align manifests and lineage without destructive code convergence.
3. **Bridge** — preserve repo boundaries and mediate integration through explicit contracts and evidence.
4. **MEGA pipeline** — orchestrate member workflows through a common CI/CD spine only after lower-tier evidence is green.
5. **Shared infrastructure / K8s** — deferred side-entry backbone, not an assumed core.

The repeated control principle is: **no tier skipping and no CI bypass**. Failed or unsuitable checks should be repaired or revised with evidence rather than ignored.

## GEMINI scaffold / wave model

The capture proposes using GEMINI first as a scaffold-discovery and wave-tracking surface:

- wave-0 = read-only scaffold discovery;
- `Case_Study/` and `Test_Cases/` become the evidence engine for later waves;
- `wave-tracker.yaml` and claimed-vs-actual tracking carry forward/backward convergence;
- federation build remains deferred until case-study evidence justifies escalation.

The source also records a later state update that GitHub Pages was enabled from `main/docs`, while a committed `/docs/index.html` and runtime evidence remained the next practical delta.

## Workspace operating model proposed

A separate cross-cutting proposal introduces a persistent federation workspace with four conceptual layers:

- L0 Governance — templates, standards, RTM, DMAIC, federation rules;
- L1 Workspace — local VS Code / agent tooling / Python environment / bootstrap;
- L2 Repositories — CODEX, GEMINI, ABACUS, ARTSTYLE, QPLANT and future members;
- L3 Runtime — CI, CD, Pages, dashboards and federation metrics.

The proposal explicitly says Git/GitHub should hold persistent artifacts; planning agents should not become storage systems.

## High-value reusable ideas

The following concepts are worth retaining as design candidates, subject to current-repo comparison:

- evidence-gated wave progression;
- explicit repo identity and boundary records;
- small PRs and reversible changes;
- runtime evidence emitted as machine-readable artifacts;
- hosted HTML/Pages as a human-facing portal rather than source authority;
- workspace recovery from a manifest rather than chat memory;
- PR packages separating architecture/planning from implementation;
- purpose-based inputs instead of a single undifferentiated `MASTER_INPUT` dump;
- federation escalation only when measured evidence justifies it.

## What is not proven by this capture

- that GEMINI has the proposed scaffold directories;
- that any proposed workflows were committed or enabled;
- that the Pages portal rendered successfully;
- that `workflow_call`, bridge contracts or a MEGA pipeline were implemented;
- that branch-protection assumptions match current repository settings;
- that proposed workspace branch conventions are valid for every member repo;
- that any proposed evidence schema is the current canonical schema.

## Risks / open questions

1. The planning text mixes CODEX, GEMINI and federation-wide concerns; present ownership must be checked before implementation.
2. Several proposed artifacts may duplicate newer SSOT/governance/metrics surfaces.
3. Historical Pages and workflow assumptions require currentness verification.
4. The workspace standard should be federated into existing governance rather than becoming a parallel authority.

## Next gate

Before implementing any part of this design candidate:

1. compare it against current CODEX/GEMINI/ABACUS governance and runtime surfaces;
2. identify overlap vs genuine gap;
3. retain only the non-duplicating delta;
4. bind an owning repo and acceptance predicate for each retained item.

## Provenance and authority boundary

This is an editorially reorganized design extract. Embedded assistant proposals were treated as proposals, not facts. The raw source remains immutable provenance and this rewrite creates no implementation or authority credit.
