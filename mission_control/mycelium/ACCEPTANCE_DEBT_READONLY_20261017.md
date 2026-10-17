# Acceptance debt read-only consumer - 17 October 2026

**Scope:** GBOGEB/CODEX. This is a bounded, non-admitting consumer of a separate ABACUS source-bound acceptance projection. ABACUS #1929 remains evidence owner, ABACUS #1860 remains merge-admission authority. CODEX #977 and QPS engineering control retain their independent responsibilities.

- Strict caller-supplied **trusted** SHA256 input and exact producer/consumer source-heads; same payload must not pass against a changed head. Hash equality verifies integrity only, not authentication.
- Read-only consumer generates a deterministic review receipt with `merge_admission=HOLD`, `root_closure_credit=0`, `authority_transfer=false` and `security_waiver=false`.
- Rejects unsupported reviewer attestation, upstream PASS, missing/forged source contexts, stale main and diff coverage, bad epochs, and schema mismatch.
- Run locally: `python -m unittest discover -s tests -p test_acceptance_debt_consumer_readonly.py -v`.
- No HTTP requests, runner dispatch, GitHub credentials, policy writes, automatic acceptance, canonical BD ledger mutation, or main merge.

**Source:** [ABACUS draft PR #2105](https://github.com/GBOGEB/ABACUS/pull/2105); its local P1/P2/P3 processing pulses are not native CODEX/QPS verification.

**DoV:** native exact-head unittest and contract first, independent owner adoption next, trust-channel/source attestation and path-disjoint lease later. Use a distinct PR; do not infer protected-main admission from this consumer parser.
