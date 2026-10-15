# CODE PURPLE KEB side-load v1

CODEX owns only semantic transport. QPS retains engineering ACCEPT/REJECT/DEFER; DOW owns QPLANT runtime evidence. No Kubernetes deployment or new publisher is introduced into CODEX.

Files: CONTRACT_V1.json is the common field/enum contract, scripts/qps_sideload_v1.py is a pure stdlib read-only envelope validator, tests/test_qps_sideload_v1.py supplies adversarial regressions.

Usage: python scripts/qps_sideload_v1.py --input candidate.json --out receipt.json [--artifact-root /path/to/sanitized/bytes]

The validator hashes any explicitly provided local sanitized file and emits metadata only. Structural PASS or LOCAL_HASH_MATCH_ONLY are never native CI authentication, cluster API proof, workload proof, peer review, edge qualification or child acceptance. Runtime provenance must be independently verified from exact run/job/attempt, artifact byte identity, and true cluster/health receipts. Zero executed steps is NOT_EXECUTED, not an application failure.

This is a transport candidate until exact-head native CI and review. Never copy bidder originals, secrets, kubeconfig, tokens or raw logs into source control. No formal engineering credit.
