# Orchestration PR Operating Contract

## 1. Intent

Establish a minimal, review-first TypeScript orchestration runtime with auditable SHA-workflow recovery notes and dependency-backed route validation.

## 2. Goal

A secret-free orchestration scaffold exposes `GET /jobs` and `POST /federation/event`, documents the SHA/update recovery state, and runs TypeScript build plus HTTP route tests in CI once npm/GitHub network access is available.

## 3. Scope

- **In scope:** `orchestration_ts/`, `handover/CURRENT.json`, `CODEX_EXECUTION_REPORT.md`, and the orchestration TypeScript CI workflow.
- **Out of scope:** live GitHub Contents API mutation from this blocked environment, production persistence, authentication, queue backends, deployment, and real `.env` files.
- **Boundary rule:** if follow-up work requires credentials, remote writes, or production behavior beyond the bootstrap routes, stop and emit a blocker instead of expanding this PR.

## 4. Definition of Victory

The PR is ready for human review only when every item below is true at the same time.

| ID | Criterion | Status |
| --- | --- | --- |
| V1 | Git status is clean after the final hardening commit. | Pending final local check |
| V2 | No secrets or live `.env` files are present. | Locally checkable |
| V3 | `.env` handling is documented and real `.env` files remain ignored. | Satisfied by `README.md`, `env.template`, and root `.gitignore` |
| V4 | `GET /jobs` and `POST /federation/event` are wired through `src/server.ts`. | Satisfied locally |
| V5 | Functional HTTP route tests exist for both runtime routes. | Satisfied locally; execution blocked until dependencies install |
| V6 | No hand-written Express ambient declarations mask missing dependencies. | Satisfied locally |
| V7 | `npm run build` passes against real installed dependencies. | Blocked: npm registry returned HTTP 403 |
| V8 | `npm test` passes and executes the HTTP route tests. | Blocked: npm registry returned HTTP 403, so `tsx` is unavailable |
| V9 | Remote branch and PR are visible on GitHub. | Blocked: `git ls-remote` returned CONNECT tunnel HTTP 403 |
| V10 | Every skipped verification is labeled `ENVIRONMENT-LIMITATION`. | Satisfied in this document and execution report |
| V11 | A repeatable network diagnostic exists for npm/GitHub 403 recovery. | Satisfied by `npm run diagnose:network` |

**Current status:** BLOCKED — not ready to merge.

## 5. Work-Until Stop Condition

Work stops when the Definition of Victory is met or an explicit blocker is hit. This PR is currently stopped at environment blockers for npm registry access and GitHub remote verification.

## 6. Review Milestones and Hold Points

- **Review milestone:** this document and `CODEX_EXECUTION_REPORT.md` identify the exact remaining validation steps.
- **Hard hold-point:** do not merge until V7, V8, and V9 pass in an environment with npm registry and GitHub access.

## 7. Sequence vs Parallel Plan

- **[SEQ] Dependency validation:** if registry access fails, run `npm run diagnose:network`; then restore npm access, run `npm install`, run `npm run build`, then run `npm test`.
- **[SEQ] Remote validation:** restore GitHub access, push the branch, verify the remote branch/PR, then allow CI to run.
- **[PAR] Review validation:** review route code, README, env-template handling, and report accuracy while environment blockers are being resolved.

## 8. Feedforward / Feedback Loop

- **Feedforward:** next operator receives the route contract, exact validation commands, `npm run diagnose:network`, and known environment limitations before continuing.
- **Feedback:** after dependency and remote validation, update `CODEX_EXECUTION_REPORT.md` with pass/fail outcomes and commit/CI links.

## 9. Reporting Format

Every follow-up cycle should report:

- action taken and commit hash;
- victory checklist delta;
- `[SEQ]` / `[PAR]` status per active track;
- feedforward emitted and feedback received;
- milestone or hold-point reached;
- open blockers, with each skipped check labeled `ENVIRONMENT-LIMITATION`.
