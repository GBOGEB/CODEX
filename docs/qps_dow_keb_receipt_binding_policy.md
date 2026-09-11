# QPS / DOW / KEB Receipt Binding Policy

Purpose: ensure future QPS, DOW and KEB receipts can be traced to exact source PR, commit SHA and file digest.

## Minimum binding tuple

Every promoted receipt should carry:

```text
source_repo
source_pr
source_sha
source_locator
file_digest
receipt_id
validation_result
downstream_consumer
```

## Promotion rule

- `PASS` or `ACCEPT` requires source PR, source SHA and file digest.
- `DEFER` may carry `TBD` digest only when the next action explicitly says to compute and bind the digest.
- `REJECT` requires the predicate or validation failure that caused rejection.

## QPS rule

QPS ranking, BT/PCA inputs and decision objects must not consume evidence that has no source locator or receipt binding.

## DOW rule

DOW must not record `ACCEPT` unless upstream proof is source-bound and exact-SHA bound.

## KEB rule

KEB must not promote knowledge from text memory alone. A KEB atom needs a source receipt, exact SHA, digest, replay proof or controlled DEFER reason.

## Draft versus strict validation

Use draft mode during early capture:

```bash
python scripts/validate_bridge_rows.py
```

Use strict mode before promotion:

```bash
python scripts/validate_bridge_rows.py --strict
```

Strict mode treats `TBD` as missing.
