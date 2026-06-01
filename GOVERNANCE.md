# CODEX Governance & Operating Model

> **Status:** PR-1 of the CODEX Federation Governance Runtime stabilization plan.
> This document defines repository identity, the operating model, and the
> workflow → lane map. It is **documentation only** — it introduces no behavior
> change to existing workflows. Subsequent PRs (PR-2..PR-5) implement the
> structural changes this document describes.

## 1. Repository identity

CODEX is a **governed federation-runtime repository**. Its operating contract is:

- **CI is the truth-verification gate.** No artifact is considered valid until it
  passes the CI validation lane.
- **Pages is the human-facing runtime portal.** Only verified, traceable,
  manifest-registered HTML is published.
- **DMAIC is the iteration ledger.** Each iteration/check cycle is recorded as
  measurable operational evidence.
- **Bridge/federation outputs are the measurable integration layer.** Integration
  is contract-driven and evidence-backed.

### What CODEX is

- A governed runtime that produces **evidence** and a **portal**.
- The source of truth (SSOT) for manifests, lineage, DMAIC phase maps, and
  bridge contracts.

### What CODEX is *not*

- Not a loose collection of one-off scripts.
- Not a shared infrastructure / Kubernetes host. Broader infrastructure
  integration is **deferred** until runtime evidence proves an immediate
  dependency.

### Primary vs secondary functions

| Tier | Functions |
| --- | --- |
| **Primary** | Governed runtime + validation evidence + human-facing portal |
| **Secondary** | Generators, visualizations, bridge/federation adapters |
| **Non-core (deferred)** | Shared infra / Kubernetes, unless runtime evidence proves immediate dependency |

### Frontend / backend split

- **Backend:** SSOT (`MANIFEST.json`, `MANIFEST/`, `maps/dmaic_phase_map.yml`,
  `bridge_manifest.yaml`, `VERSION.json`), orchestration, validation, and
  evidence emission.
- **Frontend:** the governed HTML portal under `docs/`.

## 2. Lifecycle lineage (single traceable chain)

Every published artifact must be traceable back to a governed SSOT input through
this chain:

```
Source / SSOT
  └─> Build / Orchestration
        └─> Validation / Governance (CI truth gate)
              └─> Runtime Evidence (reports/, METRICS/, outputs/html/)
                    └─> Human-facing Portal (docs/*.html)
                          └─> Federation Assimilation (bridge / rollup)
```

## 3. Workflow → lane map

The repository currently carries ~30 workflows. Each is assigned to exactly one
**primary lane** below. Lanes define responsibility, not file location; some
workflows overlap and are flagged for later consolidation.

### CI truth gate (PR / main validation)

These verify integrity of source, manifests, lineage, render governance, and
runtime contracts. They are the authoritative pass/fail signal.

- `ci.yml` — **canonical** validation gate (schemas, build, pytest,
  manifest/glob/stale/link, bridge alignment, render lint, DMAIC phase map,
  backend registry)
- `codex_semantic_runtime_ci.yml`
- `full-stack-governance.yml`
- `semantic-validation.yml`
- `delta1-governance-validation.yml`
- `render-governance-ci.yml`
- `render-parity.yml`
- `render-regression.yml`
- `renderer-lint.yml`
- `wcag-contrast.yml`
- `governance-gate.yml`
- `w003-governance-gate.yml`
- `runtime-governance-gate.yml`
- `runtime_convergence_pipeline.yml`
- `abacus-render-pipeline-smoke.yml`
- `dashboard-health.yml`

### CD / publish (Pages deploy)

These publish the human-facing portal. **Hard requirement:** deploy must depend
on CI success (see §4).

- `pages.yml` — **active deploy path** (current CD equivalent)
- `pages_deploy_runtime.yml`
- `jekyll-gh-pages.yml`
- `static.yml`
- `deploy-docs.yml`
- `update-docs.yml`
- `hbhs_ep_tuplebridge_pages.yml`
- `deploy_pipeline.yml`
- `release.yml`

### DMAIC metrics (iteration ledger)

- `dmaic-commit-metrics.yml` — per-commit tracking & feedback loop

### Bridge / federation

- `runtime_federation_ci.yml`
- `runtime_release_gate.yml`
- `receive_superpipeline_dispatch.yml`

### Advisory (review augmentation — never a truth gate)

- `agentic-pr-discrepancy-scan.yml`
- `security-scan.yml`

### Consolidation flags

The lane model surfaces overlaps to be addressed in later PRs rather than left
aspirational:

- **Multiple governance gates** (`governance-gate.yml`, `w003-governance-gate.yml`,
  `runtime-governance-gate.yml`, `full-stack-governance.yml`,
  `delta1-governance-validation.yml`) overlap with `ci.yml`. Target: converge
  into the canonical CI gate's `governance` job (PR-2).
- **Multiple Pages/deploy workflows** (`pages.yml`, `pages_deploy_runtime.yml`,
  `jekyll-gh-pages.yml`, `static.yml`, `deploy-docs.yml`,
  `hbhs_ep_tuplebridge_pages.yml`) overlap. Target: a single governed CD contract
  (PR-2 / PR-4).
- **Render lanes** (`render-governance-ci.yml`, `render-parity.yml`,
  `render-regression.yml`, `renderer-lint.yml`) overlap with the CI render-lint
  step. Target: converge under the CI `governance` job.

## 4. CI vs CD responsibilities (the workflow contract)

### CI (`ci.yml`) — validation gate

- Stays the strict PR/main validation gate.
- **Target decomposition (PR-2):** split the single `test` job into ordered jobs
  `ssot → build → test → governance → bridge → dmaic`, preserving every current
  check.
- Emits machine-readable validation evidence (PR-2):
  `reports/ci/validation_summary.json`, `reports/ci/check_timing.json`,
  `reports/ci/failure_catalog.json`.
- Fails fast on SSOT violations but **preserves artifacts for diagnosis**.
- Every failure must be attributable by **stage + artifact + owning domain**, and
  partial-success states explicitly classified (pass / fail / degraded).

### CD (`pages.yml` / future `cd.yml`) — publish gate

- **Deploy requires successful CI evidence** (`workflow_run` / `needs` gating).
- Builds the verified portal only from governed sources; stages only approved
  `docs/` + `outputs/` content.
- Re-checks manifest/stale/link rules before publish.
- Publishes a runtime evidence bundle alongside the portal.
- Rollback / redeploy behavior must be explicit.

## 5. Release-gate hardening contract

- **No Pages publish without successful CI evidence.**
- **No bridge promotion without alignment + health pass.**
- **No new HTML entrypoint without `MANIFEST.json` registration** (enforced today
  by `scripts/check_stale.py`).
- `docs/index.html` links must stay within `docs/` or be external URLs (no `../`).

## 6. PR sequencing

This document is **PR-1**. The remaining slices are independently mergeable and
must not break governance lineage:

| PR | Scope |
| --- | --- |
| **PR-1** | Repo identity + workflow contract (this document) |
| **PR-2** | CI job decomposition (`ssot/build/test/governance/bridge/dmaic`) + machine-readable evidence artifacts |
| **PR-3** | DMAIC closed-loop: per-stage iteration records + claimed-vs-actual tracking (`METRICS/dmaic/*.json`) |
| **PR-4** | Portal consolidation: `docs/index.html` as the single verified navigation hub |
| **PR-5** | Federation assimilation gate: bridge health, rollup evidence, promotion criteria (`reports/bridge/*`, `reports/federation/*`) |

## 7. Acceptance criteria (whole programme)

1. CI failures are diagnosable by artifact, stage, and owning domain.
2. CD/Pages never publishes unverified or unregistered HTML outputs.
3. DMAIC tracks each iteration/check cycle with measurable deltas.
4. Claimed completion and actual completion are compared automatically.
5. Bridge/federation integration is contract-driven and evidence-backed.
6. Repo identity is explicit enough to prevent scope drift.
7. `docs/index.html` functions as the stable human-facing runtime portal.
8. Small PRs can progress independently without breaking governance lineage.

## 8. Related documents

- `LINEAGE_BUILD_DEPLOY_CICD.md` — one-cycle build/deploy/CI-CD playbook
- `GITHUB_CENTERED_SOFTWARE_DELIVERY.md` — delivery model
- `BACKBONE_POLICY.md` — backbone policy
- `GLOB_POLICY.md` — glob policy enforced by `scripts/check_globs.py`
