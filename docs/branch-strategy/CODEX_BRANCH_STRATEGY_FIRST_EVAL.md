# CODEX Branch Strategy — FIRST EVAL

Date: 2026-06-05
Repository: `GBOGEB/CODEX`
Evaluation mode: documentation-only first evaluation

## Scope and non-destructive guardrails

This document is a FIRST EVAL branch-strategy preparation artifact only.

- No branches were deleted.
- No branch was force-pushed.
- No branch protection setting was changed.
- Cleanup candidates are recommendations only and require human approval.
- This document should be reviewed through a pull request before any operational branch action is taken.

## Repo role

`GBOGEB/CODEX` should operate as the governance-first federation/orchestration hub for the wider repository federation. Its protected surface should emphasize governance policy, federation runtime registration, ADRs, templates, bridge/orchestration code, and CI/workflow gates.

## Observed branch/PR condition

### Inventory source and confidence

The current working copy has a detached HEAD checkout (no local branch refs were present), and a Git remote (`origin`) is configured, but network attempts to query GitHub from the execution environment were blocked by a `403 CONNECT tunnel failed` response, so remote branch and PR inventory could not be verified directly during this FIRST EVAL.

### Observed local branch state

| Item | Observed value | Confidence | Notes |
|---|---:|---|---|
| Local branch | `work` | High | Current checkout branch. |
| Remote branches | Not available | Low | No local remote refs were present; remote access was blocked. |
| Default branch | Expected `main` | Medium | Local merge commits repeatedly reference `main`; confirm in GitHub before settings changes. |
| Open PRs | Not available | Low | Requires GitHub PR API/UI review. |
| Closed/merged PRs | PR #203, #204, #205, #206, #207 observed in local merge history | Medium | Local history includes merge commits for these PRs. |
| Stale branches | Not available | Low | Requires remote branch age inventory. |
| Branches merged into `main` | Not available | Low | Requires remote refs and `git branch -r --merged origin/main`. |
| Branches not merged into `main` | Not available | Low | Requires remote refs and `git branch -r --no-merged origin/main`. |
| Recent branch activity | `work` at commit `df51cd6` on 2026-06-04 | High | Local log shows latest commit is a merge of PR #206. |

### Observed recent merged PR activity from local history

| PR | Source branch seen in merge subject | Local observation | First-eval disposition |
|---:|---|---|---|
| #203 | `copilot/pr-w0052-federation-dashboard` | Merged into `main` in local history | Treat source branch as archive/delete candidate after remote confirmation. |
| #204 | `copilot/w008-federation-runtime-visualization` | Merged into `main` in local history | Treat source branch as archive/delete candidate after remote confirmation. |
| #205 | `copilot/federation-impact-review` | Merged into `main` in local history | Treat source branch as archive/delete candidate after remote confirmation. |
| #206 | `copilot/anthropic-gemini-integration` | Merged into current `work` history | Treat source branch as archive/delete candidate after remote confirmation. |
| #207 | `codex/initialize-confluence-github-federation-phase-0` | Merged into current `work` history | Treat source branch as archive/delete candidate after remote confirmation. |

### CI/workflow files observed

Workflow directory `.github/workflows/` exists and contains governance, release, runtime, render, pages, security, CodeQL, semantic validation, and federation CI workflows. This is a high-protection area because workflow changes can alter release gates, deployment behavior, and governance enforcement.

Representative workflow files observed:

- `.github/workflows/ci.yml`
- `.github/workflows/codeql.yml`
- `.github/workflows/governance-gate.yml`
- `.github/workflows/runtime-governance-gate.yml`
- `.github/workflows/runtime_release_gate.yml`
- `.github/workflows/runtime_federation_ci.yml`
- `.github/workflows/full-stack-governance.yml`
- `.github/workflows/semantic-validation.yml`
- `.github/workflows/confluence-github-bridge-phase0.yml`
- `.github/workflows/pages_deploy_runtime.yml`

### Governance/docs folders observed

Governance and documentation surfaces are present across:

- `docs/`
- `docs/ADR/`
- `docs/GOVERNANCE/`
- `docs/governance/`
- `governance/`
- `governance/adr/`
- `06_arch/ADR/`
- `KEB/governance/`
- `federation/`
- `federation_runtime/docs/`
- `federation_runtime/governance/`
- `src/governance/`
- `meta_runtime/autonomous_governance/`

## Recommended branch model

CODEX should use a governance-first, wave-based governance trunk model:

- `main` is the protected governance trunk and source of truth.
- `develop` is optional and should be used only for staged integration of governance/runtime changes that are not ready for `main`.
- `wave/*` branches group coordinated governance waves and should be time-boxed.
- `feature/*`, `fix/*`, `docs/*`, `chore/*`, and `research/*` branches are short-lived PR branches.
- `archive/*` branches are read-only historical holding branches when deletion is not yet approved.

## Target branch architecture

| Branch/pattern | Purpose | Expected lifecycle |
|---|---|---|
| `main` | Governance trunk and stable federation source of truth | Permanent; protected. |
| `develop` | Integration branch for staged governance/runtime changes | Permanent or semi-permanent; protected if used. |
| `wave/W000-bootstrap` | Bootstrap governance wave | Time-boxed; archive after merged. |
| `wave/W001-soft-refactor` | Soft-refactor planning and low-risk consolidation | Time-boxed; archive after merged. |
| `wave/W002-ci-hardening` | CI, workflow, and release-gate hardening | Time-boxed; archive after merged. |
| `feature/*` | Feature work | Short-lived; PR required. |
| `fix/*` | Defect fixes | Short-lived; PR required. |
| `docs/*` | Documentation-only changes | Short-lived; PR required. |
| `chore/*` | Maintenance work | Short-lived; PR required. |
| `research/*` | Experiments/spikes | Short-lived or archived; never release source of truth. |
| `archive/*` | Human-approved preservation of old branch state | Long-lived only when explicitly approved. |

## Branch classification table

| Classification | Branches/patterns | Rationale | Required human decision |
|---|---|---|---|
| KEEP | `main`, `develop` if adopted, active `wave/*`, active PR branches | Required for trunk, integration, and active work | Confirm actual active branches from GitHub. |
| PROTECT | `main`, `develop` if adopted, release/governance wave branches while active | Protect governance, federation runtime, ADRs, templates, and workflows | Define protection rules after this FIRST EVAL. |
| MERGE CANDIDATE | Active `feature/*`, `fix/*`, `docs/*`, `chore/*` with approved PRs | Short-lived work should merge through PR review | Confirm PR status and CI. |
| ARCHIVE CANDIDATE | Completed `wave/*`, `research/*` with retained value, historical governance branches | Preserve context before deletion when uncertain | Decide archive naming and owner. |
| DELETE CANDIDATE | Remote branches already merged into `main`, especially PR #203-#207 source branches if still present | Reduce branch noise after merged PRs | Confirm no open PRs, releases, or dependent work. |
| UNKNOWN / NEEDS HUMAN REVIEW | Any branch not visible in this checkout; any branch not merged into `main`; current `work` branch | Remote inventory was unavailable in this environment | Owner must inspect GitHub branch list before cleanup. |

## Protection recommendations

Apply protection only after human review of this FIRST EVAL. Recommended protected paths and rule themes:

- Require PR review and status checks for `main`.
- Require linear or reviewed merge policy for governance-sensitive changes.
- Disable force pushes and branch deletion for `main` and any protected integration branches.
- Require CODEOWNERS or owner review for:
  - `.github/workflows/**`
  - `governance/**`
  - `docs/ADR/**`
  - `docs/GOVERNANCE/**`
  - `docs/governance/**`
  - `federation/**`
  - `federation_runtime/**`
  - `codex/**`
  - `scripts/**` governance/runtime bridge scripts
  - templates under `codex/templates/**`
- Require CI checks for governance gates, semantic validation, federation runtime checks, render checks, and security scans.

## Cleanup candidates

Cleanup must be recommendation-only during FIRST EVAL.

| Candidate | Basis | Recommended action |
|---|---|---|
| `copilot/pr-w0052-federation-dashboard` | Observed merged PR #203 | If remote branch still exists and no open PR depends on it, mark delete candidate or archive first. |
| `copilot/w008-federation-runtime-visualization` | Observed merged PR #204 | If remote branch still exists and no open PR depends on it, mark delete candidate or archive first. |
| `copilot/federation-impact-review` | Observed merged PR #205 | If remote branch still exists and no open PR depends on it, mark delete candidate or archive first. |
| `copilot/anthropic-gemini-integration` | Observed merged PR #206 | If remote branch still exists and no open PR depends on it, mark delete candidate or archive first. |
| `codex/initialize-confluence-github-federation-phase-0` | Observed merged PR #207 | If remote branch still exists and no open PR depends on it, mark delete candidate or archive first. |
| Any branch older than 90 days with no open PR | Standard stale-branch heuristic | Human review, then archive or delete. |
| Any unmerged branch with unknown owner | Risk of losing work | Keep as UNKNOWN until owner confirms. |

## Soft-refactor approach

CODEX soft-refactor work should avoid disruptive rewrites. Recommended approach:

1. Create or confirm `wave/W001-soft-refactor`.
2. Inventory governance, federation, ADR, template, workflow, and bridge-runtime files.
3. Group changes into documentation, naming, validation, and runtime-bridge increments.
4. Land small PRs with explicit rollback notes.
5. Avoid branch deletion, force-pushes, or protection changes until the cleanup plan is approved.

## Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Remote branch/PR state not visible during this evaluation | Branch classifications may be incomplete | Re-run inventory with GitHub access before cleanup. |
| Governance and workflow files are highly coupled | Accidental CI or release-gate breakage | Require workflow/governance owner review. |
| Historical wave or research branches may contain context | Premature deletion could lose institutional memory | Prefer `archive/*` until owners approve deletion. |
| Current local branch is `work`, not confirmed `main` | PR base/default branch assumptions may be wrong | Confirm default branch in GitHub UI/API before settings changes. |

## Next actions

1. Review this document in a documentation-only PR.
2. Re-run remote inventory from an authenticated environment:
   - `git remote -v`
   - `git fetch --all --prune --dry-run`
   - `git branch -r --sort=-committerdate`
   - `git branch -r --merged origin/main`
   - `git branch -r --no-merged origin/main`
   - `gh pr list --state open`
   - `gh pr list --state merged --limit 100`
3. Confirm default branch and active owners.
4. Approve or adjust branch classifications.
5. Only after approval, create archive branches or delete stale merged branches through standard non-force operations.
6. Draft branch protection settings separately; do not apply settings as part of FIRST EVAL.

## ASCII workflow

```text
START
|
v
Inventory branches + PRs
|
v
Classify branches
|
+--> KEEP
+--> PROTECT
+--> MERGE CANDIDATE
+--> ARCHIVE CANDIDATE
+--> DELETE CANDIDATE
|
v
Create branch strategy document
|
v
Open PR for human review
|
v
NO DELETE / NO FORCE PUSH / NO SETTINGS CHANGE
```
