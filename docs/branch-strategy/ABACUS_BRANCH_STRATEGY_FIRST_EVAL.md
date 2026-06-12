# ABACUS Branch Strategy — FIRST EVAL

Date: 2026-06-05
Repository: `GBOGEB/ABACUS`
Evaluation mode: documentation-only first evaluation

## Scope and non-destructive guardrails

This document is a FIRST EVAL branch-strategy preparation artifact only.

- No branches were deleted.
- No branch was force-pushed.
- No branch protection setting was changed.
- Cleanup candidates are recommendations only and require human approval.
- This document should be reviewed through a pull request before any operational branch action is taken.

## Repo role

`GBOGEB/ABACUS` should operate as the execution/runtime repository in the federation. Its protected surface should emphasize runtime code, CI/CD, QPLANT assets, release documentation, workflow files, and runtime validation artifacts. CODEX may coordinate governance, but ABACUS should preserve runtime execution integrity and release discipline.

## Observed branch/PR condition

### Inventory source and confidence

The ABACUS repository was not present in this execution workspace, and no authenticated GitHub CLI was available. Network attempts to query GitHub from the execution environment were blocked by a `403 CONNECT tunnel failed` response, so remote branch and PR inventory could not be verified directly during this FIRST EVAL.

### Observed branch and PR state

| Item | Observed value | Confidence | Notes |
|---|---:|---|---|
| Local checkout | Not available | High | `/workspace/ABACUS` was not present in this environment. |
| Default branch | Not verified | Low | Confirm in GitHub before applying the proposed model. |
| Remote branches | Not verified | Low | Requires authenticated GitHub or clone access. |
| Open PRs | Not verified | Low | Requires GitHub PR API/UI review. |
| Closed/merged PRs | Not verified | Low | Requires GitHub PR API/UI review. |
| Stale branches | Not verified | Low | Requires remote branch age inventory. |
| Branches merged into `main` | Not verified | Low | Requires `origin/main` and remote refs. |
| Branches not merged into `main` | Not verified | Low | Requires `origin/main` and remote refs. |
| Recent activity by branch | Not verified | Low | Requires remote branch metadata. |
| CI/workflow files | Not verified | Low | Requires repository checkout. |
| Governance/docs folders | Not verified | Low | Requires repository checkout. |

## Recommended branch model

ABACUS should use an execution/runtime develop + release/wave model:

- `main` is the stable release/runtime trunk.
- `develop` is the primary integration branch for runtime and CI changes.
- `wave/*` branches coordinate bounded runtime waves such as bootstrap, soft refactor, and CI hardening.
- `release/*` may be added later if ABACUS needs versioned release stabilization beyond the requested target architecture.
- `feature/*`, `fix/*`, `docs/*`, `chore/*`, and `research/*` branches remain short-lived PR branches.
- `archive/*` is used only after human approval to preserve branch state before deletion.

## Target branch architecture

| Branch/pattern | Purpose | Expected lifecycle |
|---|---|---|
| `main` | Stable runtime and release source of truth | Permanent; protected. |
| `develop` | Runtime integration branch | Permanent; protected. |
| `wave/W000-bootstrap` | Bootstrap runtime/release hygiene wave | Time-boxed; archive after merged. |
| `wave/W001-soft-refactor` | Soft-refactor track for runtime structure, QPLANT boundaries, and low-risk cleanup | Time-boxed; archive after merged. |
| `wave/W002-ci-hardening` | CI/CD, workflow, release-doc, and runtime validation hardening | Time-boxed; archive after merged. |
| `feature/*` | Runtime feature work | Short-lived; PR required. |
| `fix/*` | Runtime defect fixes | Short-lived; PR required. |
| `docs/*` | Documentation-only changes | Short-lived; PR required. |
| `chore/*` | Maintenance work | Short-lived; PR required. |
| `research/*` | Experiments/spikes | Short-lived or archived; never release source of truth. |
| `archive/*` | Human-approved preservation of old branch state | Long-lived only when explicitly approved. |

## Branch classification table

| Classification | Branches/patterns | Rationale | Required human decision |
|---|---|---|---|
| KEEP | `main`, `develop`, active `wave/*`, active PR branches | Required for stable runtime, integration, and active work | Confirm actual active branches from GitHub. |
| PROTECT | `main`, `develop`, active `wave/*` when carrying release/runtime scope | Protect runtime, workflows, QPLANT, release docs, and CI/CD | Define protection rules after this FIRST EVAL. |
| MERGE CANDIDATE | Active `feature/*`, `fix/*`, `docs/*`, `chore/*` with approved PRs | Short-lived work should merge through PR review | Confirm PR status and CI. |
| ARCHIVE CANDIDATE | Completed `wave/*`, old `research/*`, old release-candidate branches with retained evidence | Preserve context before deletion when uncertain | Decide archive naming and owner. |
| DELETE CANDIDATE | Branches already merged into `main` or `develop` and not tied to releases/open PRs | Reduce branch noise after merged work | Confirm no open PRs, tags, releases, or dependent work. |
| UNKNOWN / NEEDS HUMAN REVIEW | All currently unverified ABACUS branches | ABACUS remote inventory was unavailable in this environment | Owner must inspect GitHub branch list before cleanup. |

## Protection recommendations

Apply protection only after human review of this FIRST EVAL. Recommended protected paths and rule themes:

- Require PR review and status checks for `main` and `develop`.
- Disable force pushes and branch deletion for protected branches.
- Require CI/CD status checks for runtime validation and release readiness.
- Require owner review for:
  - `.github/workflows/**`
  - runtime source directories, once confirmed in checkout
  - QPLANT directories/assets, once confirmed in checkout
  - release documentation directories, once confirmed in checkout
  - CI/CD scripts and deployment configuration
  - runtime schemas, manifests, and validation fixtures
- Require docs/release signoff for changes that affect release notes, versioning, QPLANT evidence, or runtime acceptance criteria.

## Cleanup candidates

Cleanup must be recommendation-only during FIRST EVAL. Because ABACUS remote inventory was unavailable, the initial cleanup table is rule-based rather than branch-name-specific.

| Candidate rule | Basis | Recommended action |
|---|---|---|
| Any branch already merged into `main` and older than 30 days | Low-risk branch hygiene | Human review, then delete or archive. |
| Any branch already merged into `develop` and older than 30 days | Integration hygiene | Human review, then delete or archive. |
| Any stale branch older than 90 days with no open PR | Standard stale-branch heuristic | Owner review, then archive or delete. |
| Any old `research/*` branch with useful runtime evidence | Research may contain context | Archive under `archive/research/...` before deletion. |
| Any old release or QPLANT branch | May be tied to release evidence | Keep until release owner approves archive/delete. |
| Any unmerged branch with unknown owner | Risk of losing work | Keep as UNKNOWN until owner confirms. |

## Soft-refactor approach

ABACUS soft-refactor work should preserve runtime behavior and avoid disruptive rewrites. Recommended approach:

1. Create or confirm `develop` as the integration branch.
2. Create or confirm `wave/W001-soft-refactor` for bounded refactor planning.
3. Identify runtime, QPLANT, release docs, workflow, and CI/CD ownership boundaries.
4. Prefer incremental compatibility-preserving refactors over large rewrites.
5. Require runtime smoke tests and CI checks for every PR.
6. Keep release documentation current with each runtime-facing change.
7. Avoid branch deletion, force-pushes, or protection changes until the cleanup plan is approved.

## Risks

| Risk | Impact | Mitigation |
|---|---|---|
| ABACUS checkout and remote inventory were unavailable | Branch classifications are incomplete | Re-run inventory from an authenticated checkout before cleanup. |
| Runtime and QPLANT assets may be release-critical | Premature branch deletion could lose release evidence | Require release owner approval before archive/delete. |
| `develop` may not currently exist | Proposed model may require branch creation | Confirm branch model with maintainers first. |
| CI/CD topology is unverified | Protection recommendations may miss required checks | Inventory workflows before applying branch protection. |

## Next actions

1. Review this document in a documentation-only PR.
2. Re-run remote inventory from an authenticated ABACUS checkout:
   - `git remote -v`
   - `git fetch --all --prune --dry-run`
   - `git branch -r --sort=-committerdate`
   - `git branch -r --merged origin/main`
   - `git branch -r --no-merged origin/main`
   - `gh pr list --state open`
   - `gh pr list --state merged --limit 100`
3. Confirm default branch and whether `develop` already exists.
4. Confirm runtime, QPLANT, release-doc, and CI/CD owner groups.
5. Approve or adjust branch classifications.
6. Only after approval, create archive branches or delete stale merged branches through standard non-force operations.
7. Draft branch protection settings separately; do not apply settings as part of FIRST EVAL.

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
