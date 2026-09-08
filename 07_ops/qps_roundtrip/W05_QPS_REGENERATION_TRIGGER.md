# W05 QPS regeneration execution trigger

This file intentionally touches `07_ops/qps_roundtrip/**` after PR #482 merged the W05 QPS Roundtrip Regeneration Zero-Delta workflow into `main`.

Purpose:

- trigger `.github/workflows/w05-qps-roundtrip-regeneration-zero-delta.yml` from an existing default-branch workflow definition;
- produce `release/SHA256SUMS`, `release/REBUILD_LOG.yaml`, and `release/ZERO_DELTA_RECEIPT.yaml` as an uploaded workflow artifact;
- avoid claiming production-builder parity from the synthetic builder.

Boundary:

- synthetic two-pass zero-delta may be claimed only if the workflow run passes and the artifact receipt says PASS;
- production-builder parity remains NOT YET until the production builder runs under the same contract.
