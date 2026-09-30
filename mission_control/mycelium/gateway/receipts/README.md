# Authenticated gateway receipts

This directory contains machine-readable receipts emitted by governed MissionControl gateway executions.

For transport v0.1, a receipt with decision `AUTHORIZE` proves only that an authenticated GitHub Actions principal presented a schema-valid, exact-head, allow-listed **STAGE_ONLY** request.

It does **not** prove repository mutation, engineering acceptance, formal credit, or remote-authority transfer.

The first transport implementation is intentionally read-only. `APPLY_BOUNDED_CODEX` remains disabled until a separately governed bounded-apply slice is implemented and proven.
