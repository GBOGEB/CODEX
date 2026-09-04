# CLAUDE.md — GBOGEB/CODEX

Operating rules for Claude Code sessions in this repository. These encode REX
(lessons learned) from prior CI triage work. Follow them without being asked.

> **Provenance note (2026-09-04):** this file did not previously exist inside
> the CODEX repository itself — the same content had only ever been checked
> into a separate working tree (Master_Input, which is actually the ABACUS
> repo). Anyone cloning CODEX fresh from GitHub saw none of these rules. This
> copy is the first one committed to CODEX's own history; the "Current
> state" section below has been corrected to match CODEX's actual HEAD as of
> this commit — keep it updated here going forward, not only in Master_Input.

## Scope

These rules apply to **CODEX only**. ABACUS has its own conventions — never
carry assumptions between the two repos; open a separate session in the
ABACUS working tree for ABACUS work.

## CI triage order

Gates fail downstream of their true cause. Always triage in this order, and
fix the earliest failing stage first:

1. **ruff** (lint)
2. **tests** (pytest)
3. **artifact validators**
4. **governance-gate**
5. **scan-pr**

A red governance-gate or scan-pr is usually a symptom, not the disease. Do
not patch a downstream gate while an upstream stage is red.

> As of 2026-09-04, ruff is pinned (`ruff==0.16.6`) and now runs as a
> report-only step in `ci.yml`, but is **not yet a blocking gate** — a
> full-repo run currently surfaces ~1,000 pre-existing violations under
> ruff's default rule set that predate this pin. Promoting the step to
> blocking is tracked as a follow-up once that backlog is triaged; until
> then, "ruff first" means "read the ruff step's output first," not "a red
> ruff step fails the build."

## Dependency pinning discipline

- **Never hard-pin build tooling.** No exact pins on setuptools, pip, wheel,
  or similar (`setuptools==X.Y.Z` broke every branch once). Use floors:
  `setuptools>=68.0`.
- **Do pin linters and renderers exactly.** ruff and Inkscape must be pinned
  to exact versions, otherwise lint and render-golden results drift between
  local and CI.
- Avoid restrictive upper bounds on test plugins (e.g. pytest-json-report)
  unless a real incompatibility is documented in the PR description.

## Paths

- All scripts and workflows resolve paths **relative to the repo root via
  pathlib** (e.g. `Path(__file__).resolve().parents[N]`). Never depend on
  the current working directory — CI working dirs differ from local.
- Create output directories before writing
  (`path.mkdir(parents=True, exist_ok=True)`); a missing `docs/rendered_outputs`
  has failed CI before.

## Artifacts and baselines

- **RTM/SSOT artifacts regenerate in the same PR** as the change that
  invalidates them — never in a follow-up PR.
- **Render golden baselines change deliberately**: a baseline update is its
  own reviewed commit with a one-line justification, never a side effect.
- Maintain the **secret-scan allowlist** — add documented false positives to
  it rather than restructuring code to dodge the scanner.

## PR discipline

- **One root cause per PR.** If triage reveals two independent causes, split
  them. Mixed-cause PRs are why the backlog got hard to merge.
- Before claiming a change is isolated from CI ("this only touches docs"):
  check the changed files are not **workflow_call or composite-action
  targets** of other workflows. Scope claims precisely ("independent of the
  test pipelines") — never categorical ("doesn't affect CI").
- **"Mergeable / 0 behind" does not mean main is green.** Before asserting a
  failure pre-exists on main, link an actual main-branch workflow run that
  shows it.
- Warning about auto-commit or `[skip ci]` loops requires naming the **exact
  trigger** (workflow + event) — no vague loop warnings.
- Scanner failures (e.g. Bandit non-zero) have multiple failure modes:
  real findings vs. bad `-c` config path vs. missing target directory.
  **Read the log before asserting which one it is.**

## Reporting honesty

- A test stage that runs **zero tests is a failure, not a pass**. Never
  report "all tests passing" on an empty result set, and fix any workflow
  that does.
- When summarizing CI status, distinguish **passed / failed / skipped /
  not-required**. "Green checkmark" alone is not evidence.
- The governance snapshot emitted by `scripts/emit_governance_snapshot.py`
  had a real bug until 2026-09-04: it compared step status against the
  literal string `"passed"`, but every workflow feeds it GitHub Actions'
  actual `steps.<id>.outcome` values (`success`/`failure`/`skipped`), so
  every check had always recorded as failed regardless of true CI outcome.
  Fixed by normalizing `success`→`passed`/`failure`→`failed` on parse. If
  you add a new `--check name=${{ steps.X.outcome }}` call anywhere, this
  is already handled — no per-callsite mapping needed.

## Current state (2026-09-04 — update as merged)

- PR **#234** (`fix/ci-dependency-failures`) is confirmed merged (commit
  `e92b9ed`, 2026-06-15) and is an ancestor of current HEAD. The repo-wide
  red-check incident it fixed is long resolved.
- HEAD is currently `45c3b35` (2026-08-31), ~2,143 commits into `main`. The
  active workstream is the QPS wave-based DOW/KEB bidder-evaluation series
  (W05 and later), not the convergence/maturity-tracker approach referenced
  in older DMAIC-era planning docs — see ABACUS's own
  `DMAIC_V3_TO_V4_ROADMAP.md` for that separate, largely-superseded thread.
- No file literally named `main.py` exists in this repo. The closest
  equivalent is `abacus_pid_pipeline/__main__.py` (a thin shim into
  `scripts/extract_pid_semantics.py`) — a one-shot, stdlib-only, no-network
  P&ID semantic-model extractor. Treat any future "add a main.py" request
  as "which of the ~9 root-level `orchestrate_g*.py` scripts, or this one,
  did you actually mean" rather than assuming a single canonical entry
  point exists.
