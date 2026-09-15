# QPS Debug Global Federation — CODEX/KEB

CODEX is the semantic KEB authority for the QPS debug envelope; it is not the producer of QPS runtime truth.

## Producer chain

`cryoplant/QPS TRIAGE -> debug_keb_export.json -> CODEX/KEB binding -> ABACUS/DOW -> child disposition`

The KEB consumer is fail-closed. It can return `ACCEPT` only when the QPS envelope identifies `GBOGEB/cryoplant-project`, carries a non-UNKNOWN exact head SHA, reports producer `ACCEPT`, proves runtime steps > 0, and reports recursive audit PASS.

A missing envelope, historical-only receipt, runner-assignment blocker, zero-step execution, or DEFER producer state remains `DEFER` in CODEX.

## DAG boundary

The QPS runtime Debug DAG remains a second DAG. It does not replace or overload `semantic_substrate/branch_dag.yaml`. CODEX may bind runtime evidence to semantic authority, but runner/session/port/container lifecycle remains runtime-DAG state.

## Authority guard

KEB debug binding does not change QPS formal engineering or negotiation credit.
