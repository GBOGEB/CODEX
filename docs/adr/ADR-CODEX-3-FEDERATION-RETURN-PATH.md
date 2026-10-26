# ADR-CODEX-3: Federation return path for cross-repo census results

## Status

**Proposed — owner to accept.** Nothing in this ADR changes a workflow, a
secret or a repository setting. It records the comparison and recommends a
default. Refs GBOGEB/CODEX#1199 (part b).

## Context

Evidence read on 2026-10-26, read-only, at pipeline-automation-hub `master`
`3ed30b2b9ae53a24ec72780b4e01df484c0fb591` and CODEX `main`
`d6a0b080e5c8173e706e68c23a2ddae5b1dc96d3`.

**Outbound (hub to producer) is `workflow_dispatch`.**
`tools/metric-atlas/metric_atlas/dispatch.py` posts to
`repos/<producer>/actions/workflows/qps-metric-census-receiver.yml/dispatches`
with `ref: main` and exactly four inputs (`wave`, `selector`, `request_id`,
`expected_sha`). It runs only from hub `master`, only on a
`workflow_dispatch` event, and only with `QPS_DISPATCH_APPROVED=YES`. The
fine-grained `QPS_TRIAGE_DISPATCH_TOKEN` needs **Actions: read and write**
on the receivers, and nothing more. `repository_dispatch` was dropped because
it needs Contents: write, which can also push code. The API answers HTTP 204,
and the hub records that as `HTTP_204_EVENT_ENQUEUED_NOT_PROVEN_EXECUTED`.
The 204 carries no run ID.

**Return (producer to hub) is a consumer pull.** The CODEX receiver
(`.github/workflows/qps-metric-census-receiver.yml`, permissions
`contents/actions/checks: read`) calls the hub's reusable receiver, pinned to
`dd606d88…`. That uploads one artifact per route,
`qps-metric-<route>-<run_id>-<run_attempt>`, with `retention-days: 21`.
Nothing is pushed back. An operator downloads the ZIPs and runs
`metric_atlas/postflight.py --verify-native`, which does three things:

- re-reads `actions/runs/<id>` and `actions/jobs/<id>` through an
  independently authenticated `gh api`;
- checks run ID, attempt, job ID, `head_sha`, trigger, workflow path and
  terminal conclusion against the receipt;
- opens the ZIP without extracting it, requires exactly one member
  `<route>.json`, checks the CRC, and requires the member bytes to equal the
  receipt.

Every gap becomes a named `HOLD_*` state, and `merge_admission` stays
`HOLD`. See the hub's `tools/metric-atlas/docs/QPS_N3_POSTFLIGHT_CONTRACT.md`.

Two older CODEX receivers, `receive_superpipeline_dispatch.yml` and
`qps-debug-federation-consumer.yml`, still accept `repository_dispatch` or
`pull_request` and return only by artifact.

**Platform constraint.** A `workflow_run` trigger fires only for workflows
in the *same* repository. The hub cannot subscribe to a CODEX run
completing. Any hub-side "pull" across repositories is therefore a poll of
the Actions API (`gh run list` / `gh run download`), operator-run or
scheduled, never an event.

## Options compared

| | (1) Consumer pull of artifacts | (2) PR-comment transport | (3) Committed receipt, consumer polls | (4) GitHub App token for cross-repo dispatch |
|---|---|---|---|---|
| **What moves** | Hub reads producer run and job metadata and the artifact ZIP through the Actions API | Producer job posts the receipt as a comment on a hub PR or issue | Producer job commits `receipts/<request_id>.json` to a branch; hub polls Contents | Credential, not a transport. A short-lived installation token replaces the PAT for outbound, and could let the producer dispatch a hub "results-ready" workflow |
| **Producer needs** | Nothing beyond `actions: read` in its own repo (it already has it) | A token with Issues or PR **write** on the hub, stored as a producer secret | **Contents: write** somewhere, which `dispatch.py` deliberately avoided | App installed on both repos. The private key lives as a secret wherever tokens are minted |
| **Consumer needs** | Actions: **read** on producers, which is read-only | Read on its own repo | Contents: read on producers | App with Actions: read/write on the target repos only |
| **Token scope** | Narrowest. Read-only on the return leg | Wrong direction: a producer credential can write into the controller repo | Broadest: the write scope can also push code | Narrow per installation, 1-hour expiry, no human PAT. The key itself is high-value |
| **Cache poisoning / privileged `workflow_run`** | No `workflow_run` across repos (impossible). If a same-repo `workflow_run` is ever added in the hub, it must not check out or execute artifact contents, and it must treat artifact bytes as untrusted data. `postflight.py` already does this (no extraction, single member, byte-equality) | Comment text is attacker-reachable: anyone with comment access can post a look-alike, so parsing it in a privileged job is an injection surface | Receipt files are code-adjacent. A branch that can be written can poison later checkouts or caches keyed on that path | A token minted in a privileged job must never reach a step that runs PR-controlled code. Mint it in a job that checks out `github.sha` only |
| **Latency** | Poll interval plus run time. Correlation is by listing `workflow_dispatch` runs after the dispatch time, because the 204 has no run ID | Near-real-time once posted | Poll interval plus commit and push time | Push-style: producer can dispatch the hub on completion, so seconds after the run ends |
| **Failure modes** | Artifact expired (21 days); run not yet terminal; ambiguous run correlation; download auth failure. Each maps to an existing `HOLD_*` | Comment API rate limits; 65 536-character body limit; comments edited or deleted after the fact; bot-user spoofing | Push races and non-fast-forward; branch-protection rejections; history bloat; receipts drift from the run that made them | App not installed or permission not granted; key rotation; token expiry mid-job |
| **Audit trail** | Strong. The run, job, attempt, `head_sha` and artifact digest are platform-issued and re-read independently. Weak spot: the artifact disappears after retention, so the hub must persist the ZIP SHA-256 (postflight already emits it) | Weak. Mutable, deletable, and authored by a token rather than by the run | Strong for the file (git history), weak for proving which run wrote it | Good for outbound: actions are attributed to the App. Says nothing about result integrity by itself |

## Decision (recommended)

**Adopt option 1, consumer pull, as the return path, and keep the existing
postflight verifier as its admission check.** Options 2 and 3 are rejected:
each needs a producer-side write credential into another repository, and
each has a weaker integrity story than platform-issued run metadata.
**Option 4 is recommended as a separate, later credential hardening** for
the *outbound* leg. It would replace the long-lived fine-grained PAT with
App installation tokens. It does not change the return path. Creating and
installing an App is an owner action.

Concretely, if accepted:

1. Keep `workflow_dispatch` outbound and artifact consumer pull inbound. Do
   not add a producer-to-hub write credential.
2. Fix correlation. Add a `run-name:` that contains `request_id` to the
   receiver workflows, so the hub finds the exact run with `gh run list
   --json displayTitle` rather than by time window.
3. Run the pull, `gh run download <run_id> -n qps-metric-<route>-<run_id>-<attempt>`,
   followed by `postflight --verify-native`, either by the operator or from
   a hub job with an **Actions: read** token. That job checks out
   `github.sha`, never extracts or executes artifact content, and stores the
   postflight JSON (with the ZIP SHA-256) as its own artifact or as a
   committed receipt in the hub, so the audit trail outlives the producer's
   21-day retention.
4. Migrate `receive_superpipeline_dispatch.yml` off `repository_dispatch`
   to the same `workflow_dispatch` plus artifact pattern when it is next
   touched.

## Consequences

**Positive**
- The return leg has no producer write credential at all.
- Integrity rests on platform-issued identities (run, attempt, job,
  `head_sha`) and byte equality, both of which are already implemented and
  tested in `postflight.py`.
- No new transport to build.

**Negative**
- Polling latency and the run-correlation step remain. Item 2 reduces the
  correlation risk; it does not remove the latency.
- Artifacts expire after 21 days, so a missed pull window means a
  re-dispatch.
- The outbound PAT stays until an owner sets up option 4.

## Findings recorded while writing this ADR (not fixed here)

- The hub's reusable receiver uses `actions/upload-artifact@v4` by tag, not
  by full commit SHA.
- `docs/ADR/README.md` (one tracked file) and `docs/adr/*.md` (this file and
  two others) differ only in letter case. On Windows checkouts both land in
  one folder. `docs/ADR/README.md` also names `06_arch/ADR/ADR.md` as the
  canonical ADR location; that choice is the owner's.
