# MissionControl Authenticated Execution Gateway — Design v0.1

## Purpose

Convert a staged MissionControl command envelope into an authenticated,
authorized, exact-head-bound execution request **without putting credentials or
mutation authority in GitHub Pages**.

This slice is a design/control implementation only. It does **not** enable Apply.

## Boundary

```text
STATIC HTML / COMMAND_INPUT_ROOT
        |
        | stage / dry run only
        v
governed request envelope
        |
        | authenticated transport (future bounded implementation)
        v
AUTHENTICATED EXECUTION GATEWAY
        |
        +--> bind principal server-side
        +--> refresh exact target head
        +--> authorize action class / repo / paths
        +--> enforce idempotency + replay guard
        +--> require dry-run + approval for mutation
        |
        v
bounded executor
        |
        v
append-only execution receipt
        |
        +--> evidence graph
        +--> temporal lineage
        +--> recovery checkpoint
```

## Non-negotiable guards

- Browser identity is never trusted as authentication.
- Browser secrets are forbidden.
- Static Pages remains `STAGE_OR_DRY_RUN_ONLY`.
- Default authorization is DENY.
- A mutation request must bind an exact 40-character expected head SHA.
- A changed-path allowlist is required before any future mutation.
- Completed idempotency keys cannot be replayed.
- Remote ABACUS / cryoplant authority is not mutated by CODEX by default.
- Requesting a typed remote return is not the same as mutating the remote repo.
- Every mutation-capable implementation is a separate bounded slice with its
  own exact-head proof.
- Gateway success never creates engineering/formal credit by itself.

## State machine

```text
STAGED
  -> AUTHENTICATE
  -> REFRESH_TARGET_HEAD
  -> AUTHORIZE
      -> DENY / WITHHOLD
      -> DRY_RUN
          -> APPROVAL_REQUIRED
              -> EXECUTE_BOUNDED
                  -> PROVE
                  -> RECEIPT
                  -> CONTROL
```

## Next bounded implementation slice

The design may promote to implementation only when an authenticated transport is
selected and its credential boundary is explicit. The implementation must start
with CODEX-only bounded actions; remote mutation stays denied.
