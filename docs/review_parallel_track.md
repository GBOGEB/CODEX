# Pending Review Integration Strategy (GitHub)

This pattern lets you keep delivery moving while isolating unresolved review feedback.

## Goal
- Merge a stable baseline quickly.
- Keep reviewer-requested changes decoupled until approved.
- Avoid blocking mainline release cadence.

## Branch model
1. `main` (protected): only approved, green CI changes.
2. `feature/core-topic-ep` (delivery branch): current implementation PR into `main`.
3. `review/followups-core-topic-ep` (parallel track): all review comments and refactors.

## Recommended flow
1. Open PR-A from `feature/core-topic-ep` to `main` for "merge-as-is" baseline.
2. In parallel, create PR-B from `review/followups-core-topic-ep` to `feature/core-topic-ep` (or `main`, your choice).
3. Apply all comment-driven updates in PR-B.
4. Use required checks + reviewer approvals on PR-B.
5. Merge PR-A when baseline is accepted; merge PR-B when comments are resolved.

## Waiting safely for pending review
- Use draft PR status for PR-B until implementation is complete.
- Add labels: `pending-review`, `follow-up`, `non-blocking`.
- Enable branch protection requiring:
  - 1–2 approvals
  - passing checks
  - up-to-date branch before merge
- Optionally enable auto-merge only after checks and approvals complete.

## Conflict minimization tips
- Keep PR-A small (naming/content only).
- Put structural refactors and larger code updates in PR-B.
- Rebase `review/followups-*` frequently onto latest `main`.
- Use `CODEOWNERS` for targeted reviewers by directory.

## Example commands
```bash
# baseline delivery branch
git checkout -b feature/core-topic-ep

# parallel follow-up branch
git checkout -b review/followups-core-topic-ep

# after baseline merges
git fetch origin
git checkout review/followups-core-topic-ep
git rebase origin/main
```

## Suggested policy statement
"We use dual-track PRs: baseline PRs for immediate safe merge, and follow-up PRs for comment resolution and deeper improvements."
