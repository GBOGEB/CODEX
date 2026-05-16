# GISTAU CH15 V11 — Study Notes and TODO Backlog

## Scope
This note summarizes currently available handover guidance in the local CODEX workspace and converts it into an execution-oriented TODO list for the GitHub integration cycle.

## Key findings from existing handover references

1. Integration work must be delivered as **small, testable deltas** with smoke checks and reviewer notes.
2. Existing behavior is baseline truth; modifications should be **proof-driven** and verified for parity.
3. Build outputs are expected to be **idempotent/deterministic** for same inputs.
4. Integration policy expects **parallel method retention** (A/B path) for one review cycle before convergence.
5. UI/style and engineering outputs must remain formal, high-contrast, and review-friendly.
6. Workflow expects staged integration with structured smoke/regression checks and decision logging.
7. Handover process emphasizes reproducible release snapshots and seed-tag style checkpoints.

## CH15-V11 execution TODOs

## A. Repository and branch governance
- [ ] Confirm authoritative remote is `GBOGEB/CODEX` and document access limitation for `GBOGEN/CODEX`.
- [ ] Ensure branch naming pattern and protection behavior are explicitly documented for `main` and feature branches.
- [ ] Establish integration branch lifecycle (`feature/*` -> review -> merge -> tagged snapshot).

## B. Handover artifact placement and structure
- [ ] Keep `handover/GISTAU_CH15_V11_PR_HANDOVER.md` as primary integration handover source.
- [ ] Add explicit artifact map covering `handover/`, `docs/`, and `output/` publication paths.
- [ ] Add a deterministic artifact manifest update step to the PR checklist.

## C. CI/CD and validation stages
- [ ] Add staged validation gates: lint -> smoke -> deterministic-output check -> package check.
- [ ] Add a lightweight idempotency check that compares output hashes excluding timestamp metadata.
- [ ] Include branch-level required checks to block merges when smoke checks fail.

## D. PR strategy and commit sequencing
- [ ] Enforce small-scope PRs: one integration concern per PR.
- [ ] Require PR body sections: purpose, scope, validations run, risk notes, rollback path.
- [ ] Use explicit commit sequence: scaffold -> integrate -> verify -> document -> release note.

## E. Recursive engineering lineage and TODO governance
- [ ] Classify every new item as Decision / Requirement / Assumption / Risk / Action / Evidence / Validation.
- [ ] Use status tags consistently: ACCEPT / REVIEW / RISK / TRACE / TODO / NEXT / DONE.
- [ ] Record lineage notes for each iteration: what changed, what was preserved, and why.

## F. Immediate next actions
- [ ] Import/fetch branch `ch15-v11-recursive-engineering` into local environment once remote is configured.
- [ ] Compare the branch handover file against local master-plan constraints and capture gaps.
- [ ] Create follow-up PR(s) that implement CI starter workflow and deterministic manifest checks.

## Validation log (local)
- Verified this note against existing local handover references in `99_handover/` and root workflow documents.
- This file is a planning and alignment artifact; no runtime behavior changes introduced.
