# Branch hygiene

Lossless burn-down of stale branches, census of 2026-10-11 against `main`.
244 non-default branches were classified; 1 with an open pull request
are kept and not listed.

| List | Mode | Branches |
| --- | --- | --- |
| `W1_DELETE_MERGED_20261011.tsv` | delete | 58 |
| `W2_ARCHIVE_SUPERSEDED_20261011.tsv` | archive | 152 |
| `W3_ARCHIVE_EVOLVED_20261011.tsv` | archive | 18 |
| `W4_ARCHIVE_NEVER_LANDED_20261011.tsv` | archive | 15 |

Run a list with **Actions → Branch hygiene (lossless) → Run workflow**: first with
`execute` off (dry run), then on. `scripts/branch_hygiene_delete.py` re-checks every
branch at run time and skips it unless its head is still the census SHA, it is not
protected and has no open pull request, and:

- `delete`: every commit is on `main`, or a merged pull request has this exact head
  (the commits stay reachable as `refs/pull/<n>/head`);
- `archive`: the head is first tagged `archive/<branch>` and the tag is read back.

Restore any branch with the command in the run's receipt:
`git push origin <sha>:refs/heads/<branch>` (for archived ones the tag also works:
`git push origin archive/<branch>:refs/heads/<branch>`).

Run `W4_ARCHIVE_NEVER_LANDED` only after its branches are reviewed for
unlanded fixes.

## W5 regrowth census, 2026-10-24

Branches grew back from 17 to 41 after the 2026-10-11 burn-down. Each new
branch was classified the same way, and every unmerged one was read against
`main` (3-way `git merge-tree`). The decisions and evidence per branch are in
the census ledger in the owner's project folder.

| List | Mode | Branches |
| --- | --- | --- |
| `W1_DELETE_MERGED_20261024.tsv` | delete | 6 |
| `W2_ARCHIVE_SUPERSEDED_20261024.tsv` | archive | 5 |
| `W3_ARCHIVE_EVOLVED_20261024.tsv` | archive | 3 |

Not listed on purpose:

- 4 branches whose work is re-landed by its own PR (certifi floor, Docker
  healthcheck, LF receipt writers, Mycelium observation binder). Archive them
  once those PRs merge.
- 2 branches held for the owner: `repair/20261013-postmerge-ruff-i001` adds
  an 80% changed-line admission gate, and
  `work/disjoint-census-verification-20261013` was staged with "no new PR".
- `automation/update-docs` (live automation) and 5 dependabot branches with
  open PRs.
- The 15 branches of `W4_ARCHIVE_NEVER_LANDED_20261011.tsv`: their heads are
  unchanged, and the 2026-10-12 consolidation decided every one of them, so
  that list is ready to run as it is.

Five of the W2 branches carry only a receipt commit that
`missioncontrol-inventory-autoregen.yml` pushed seconds after the PR merged;
a separate PR makes the autoregen workflow skip PRs that are no longer open.

## W8 census, 2026-10-25

All 38 branches were checked again against `main` (563a1212). No branch is
new since the W5 census apart from `automation/metrics`, and no head on a
ready list or a held branch has moved. There are no open pull requests.

| List | Mode | Branches |
| --- | --- | --- |
| `W8_ARCHIVE_SUPERSEDED_20261025.tsv` | archive | 4 |

The list holds the source branches of the W6 re-land PRs, which all merged
on 2026-10-25: #1175 (certifi floor), #1176 (Docker healthcheck), #1177 (LF
receipt writers) and #1178 (Mycelium observation binder). Their fixes are on
`main`. A 3-way merge with `main` adds only regenerable receipts or a
reworded comment.

Not listed on purpose:

- `automation/metrics` and `automation/update-docs`: live automation branches
  that their workflows force-push.
- `repair/20261013-postmerge-ruff-i001` and
  `work/disjoint-census-verification-20261013`: still held for the owner,
  heads unchanged.
- The 29 branches already on the `*_20261024.tsv` lists and
  `W4_ARCHIVE_NEVER_LANDED_20261011.tsv`: their heads are unchanged, so those
  lists are ready to run as they are.
