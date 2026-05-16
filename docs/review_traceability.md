# Review Traceability — How-To Guide

This document explains how to **tag, label, and attribute** review-driven fixes so their
source and timing are traceable across git history, pull requests, and CI/CD pipelines.

---

## Why bother?

When a code-review comment or automated scan triggers a fix, the resulting commit is
indistinguishable from a regular feature commit unless you annotate it.
Structured annotations let you:

- Query "all commits that fixed a review comment" with a single `git log` command.
- Filter CI/CD pipeline runs by review-fix status (e.g., auto-approve re-runs).
- Generate a post-merge audit report by file, reviewer, or date range.

---

## Option 1 — Git trailers in commit messages (recommended)

[Git trailers](https://git-scm.com/docs/git-interpret-trailers) are structured
`Key: Value` lines at the bottom of a commit message, separated from the body by a
blank line.  GitHub renders them in the commit view and they are parseable by
`git log --format`.

### Convention used in this repository

| Trailer | Meaning | Example |
|---|---|---|
| `Review-Fix` | Thread/discussion URL that motivated the change | `Review-Fix: https://github.com/GBOGEB/CODEX/pull/25#discussion_r…` |
| `Review-Source` | Tool or reviewer that raised the finding | `Review-Source: copilot-pull-request-reviewer` |
| `Review-Date` | ISO-8601 date the review comment was posted | `Review-Date: 2026-05-12` |

### Step-by-step

**1. Write the commit message with trailers:**

```
Fix XSS sink: replace innerHTML with createElement/textContent

All innerHTML string interpolation removed from dashboard.html render
pipeline. Hash-based CSP meta tag added as defence-in-depth.

Review-Fix: https://github.com/GBOGEB/CODEX/pull/25#discussion_r3225952582
Review-Source: copilot-pull-request-reviewer
Review-Date: 2026-05-12
```

**2. Add the trailers interactively (optional helper):**

```bash
git commit --trailer "Review-Fix: <URL>" \
           --trailer "Review-Source: copilot-pull-request-reviewer" \
           --trailer "Review-Date: $(date -I)"
```

**3. Search all review-fix commits later:**

```bash
# All commits that carry a Review-Fix trailer
git log --grep="^Review-Fix:" --format="%h %s%n  %b" | grep -A1 "Review-Fix"

# One-liner: hash + trailer value
git log --format="%h %(trailers:key=Review-Fix,valueonly)" | grep -v "^$"
```

---

## Option 2 — GitHub PR labels

Labels are queryable via the GitHub API and appear in the PR sidebar.

**Recommended label set:**

| Label | Colour | When to apply |
|---|---|---|
| `review-fix` | `#e4e669` | Any commit/PR driven by a reviewer comment |
| `copilot-remediation` | `#7057ff` | Fix applied by GitHub Copilot in response to a review |
| `security-hardening` | `#d93f0b` | XSS, CSP, secrets, or other security-review fixes |

**Apply via GitHub CLI:**

```bash
# Label the current PR
gh pr edit <PR-number> --add-label "review-fix,copilot-remediation"

# List all PRs with a given label
gh pr list --label "review-fix" --state all
```

**Apply in CI (e.g., GitHub Actions):**

```yaml
- name: Label review-fix PRs
  if: contains(github.event.pull_request.title, 'review-fix')
  run: gh pr edit ${{ github.event.number }} --add-label "review-fix"
  env:
    GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

---

## Option 3 — Git tags post-merge

After the PR is merged, tag the merge commit so the fix is findable by name:

```bash
# Tag the merge commit
git tag review/xss-csp-fix-pr25 <merge-commit-sha>
git push origin review/xss-csp-fix-pr25

# List all review/* tags
git tag -l "review/*"

# Find the commit a tag points to
git rev-list -n 1 review/xss-csp-fix-pr25
```

Use `review/<slug>-pr<number>` as the naming pattern so tags are grouped and
self-documenting.

---

## Option 4 — CHANGELOG / audit file

For teams that want a human-readable audit trail independent of git tooling, maintain
`docs/REVIEW_FIXES.md` (or append to `CHANGELOG.md`) with entries like:

```markdown
## 2026-05-12 — XSS/CSP hardening in dashboard.html

- **File:** `docs/dashboard.html`
- **Review thread:** https://github.com/GBOGEB/CODEX/pull/25#discussion_r3225952582
- **Reviewer:** copilot-pull-request-reviewer
- **Fix commit:** `1080e78`
- **Description:** Replaced `innerHTML` string interpolation with
  `createElement`/`textContent`; added hash-based CSP meta tag.
```

---

## Which option should I use?

| Situation | Recommended option |
|---|---|
| Solo or small team, full git control | **Option 1** (trailers) |
| GitHub-based workflow, need API queries | **Option 2** (labels) |
| Post-merge audit / release notes | **Option 3** (tags) |
| Compliance / external audit requirement | **Option 4** (CHANGELOG) |
| Belt-and-suspenders / regulated project | **All four** |

---

## Live example in this PR

The commit that introduced this file carries the following trailers
(run `git log --format="%B" -- docs/review_traceability.md | head -20` to verify):

```
Review-Fix: https://github.com/GBOGEB/CODEX/pull/25#discussion_r3225952582
Review-Source: copilot-pull-request-reviewer
Review-Date: 2026-05-12
```

This makes the review provenance machine-readable without touching any source file.
