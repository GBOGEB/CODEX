#!/usr/bin/env bash
# Publish bot-generated files as a pull request instead of pushing to main.
#
# main is protected by the Codex_main_protect ruleset (pull request required),
# so bots stage their output on one rolling branch per bot and keep one open PR
# for it. Each run rebuilds the branch from the current checkout (a fresh main),
# so the PR always shows the latest regeneration on top of the latest main.
#
# Usage: scripts/ci/open_bot_pr.sh BRANCH "PR title" BODY_FILE PATH [PATH ...]
# Needs: GH_TOKEN, contents: write and pull-requests: write.
# If repository policy forbids Actions from creating PRs, the branch is still
# published and the job summary says so (owner opens or enables the setting).
set -euo pipefail

branch="$1"; title="$2"; body_file="$3"; shift 3

git config user.name "github-actions[bot]"
git config user.email "github-actions[bot]@users.noreply.github.com"
git add -- "$@"
if git diff --cached --quiet; then
  echo "No tracked output changed; no bot PR needed."
  exit 0
fi

source_sha="$(git rev-parse HEAD)"
git checkout -B "$branch"
git commit -q -F "$body_file"

remote_sha="$(git ls-remote --heads origin "refs/heads/$branch" | awk '{print $1}')"
if [ -n "$remote_sha" ]; then
  git push --force-with-lease="refs/heads/$branch:$remote_sha" origin "$branch"
else
  git push -u origin "$branch"
fi

existing="$(gh pr list --head "$branch" --base main --state open --json number --jq '.[0].number // empty' || true)"
if [ -n "$existing" ]; then
  echo "Updated existing bot PR #$existing (branch $branch, source $source_sha)."
  exit 0
fi

set +e
gh pr create --base main --head "$branch" --title "$title" --body-file "$body_file"
rc=$?
set -e
if [ "$rc" -ne 0 ]; then
  {
    echo "### Bot branch published, PR not created"
    echo
    echo "Branch \`$branch\` holds the regenerated files from source \`$source_sha\`."
    echo "Repository policy did not let GitHub Actions open the PR. Either open it from the branch,"
    echo "or enable *Settings -> Actions -> General -> Allow GitHub Actions to create and approve pull requests*."
  } >> "${GITHUB_STEP_SUMMARY:-/dev/stdout}"
  echo "::warning::Bot branch $branch published; PR creation was refused by repository policy."
fi
