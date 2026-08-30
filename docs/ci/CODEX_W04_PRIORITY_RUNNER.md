# CODEX W04 priority runner lane

## Purpose

Provide a bounded interim capacity boost for governed QPS W04 KEB receipt execution while the shared GitHub-hosted Actions backlog drains.

This lane does not replace normal GitHub Actions governance and does not grant engineering, completion, PCA, BT, Table-10 or Safety credit. The resulting receipt must still be validated, artifact-bound in QPS, and dispositioned ACCEPT / REJECT / DEFER.

## Activation threshold

Enable this lane when CODEX remains at <=2 active Actions runs across consecutive queue observations while the W04 KEB receipt remains queued and the queue-per-active-slot ratio is RED (>5).

Disable/scale down when W04 is complete or CODEX returns to a sustainable hosted-runner state.

## Pool

Start with 2 ephemeral Linux x64 self-hosted workers. Scale to 4 only if both workers remain saturated and governed W04 work is still waiting.

Required labels:

- `self-hosted`
- `linux`
- `x64`
- `codex-w04`

Use ephemeral runners where practical. Give the runner identity only the repository access required to execute CODEX Actions. Do not place long-lived credentials in the repository or workflow.

## Dispatch

The normal push and pull-request W04 jobs remain on `ubuntu-latest`.

Once at least one `codex-w04` runner is online, manually dispatch `QPS W04 KEB receipt contract` from `main` with `priority_runner=true`. This selects only the dedicated priority job and prevents duplicate hosted execution for that dispatch.

Do not dispatch `priority_runner=true` before a matching runner is registered and online; otherwise the priority job will simply wait for that label.

## Evidence boundary

The priority job performs the same governed sequence as the hosted runtime lane:

1. checkout CODEX parent;
2. validate the fixture contract;
3. produce the W04 KEB runtime receipt using the bound QPS child SHA;
4. validate the produced receipt;
5. upload the run-ID-bound receipt artifact.

After success, capture run ID, artifact ID, parent SHA, child SHA, input/snapshot/output/glossary hashes, then update the QPS binding and disposition each returned finding. Only ACCEPT findings may be assimilated.

## Exit

Remove or leave dormant the priority lane after backlog recovery. It is an interim governed capacity lane, not a reason to migrate the general CODEX CI backlog to self-hosted infrastructure.
