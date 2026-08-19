# GitHub Actions Work Report Gate Scaffold

This document describes a future GitHub Actions gate for Universal Work Reports. It is intentionally scaffold-only: no workflow file is created, no active enforcement is enabled, and no PR merge behavior changes.

## Intended future checks

1. Confirm the expected report (e.g., `docs/reports/PR<PR_NUMBER>_WORK_REPORT.md`) exists for the PR under review (or another configured report path for non-PR work units).
2. Confirm a machine-readable YAML/JSON twin exists.
3. Parse the twin against `schemas/universal_work_report.schema.yaml`.
4. Verify blocker and environment-limitation fields are separate.
5. Verify `merge_allowed: false` for review-first PRs unless a human release process explicitly changes it.
6. Emit annotations only; do not merge, auto-approve, or mutate protected branch settings.

## Non-goals for this PR

- No `.github/workflows/*` enforcement file is added.
- No GitHub token or secret is accessed.
- No status check is required by branch protection.
- No auto-merge, deployment, or external API action is enabled.

## Follow-on PR feedback

FEEDBACK: If maintainers want active CI enforcement, implement it in a separate PR that includes workflow code, test fixtures, token permissions review, and human approval of branch protection changes.
