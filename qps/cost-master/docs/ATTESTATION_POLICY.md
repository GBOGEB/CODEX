# QPS COST_Master attestation policy

Control: GOV-001 / W005
Status: decision record
Date: 2026-08-28

## Decision

For the first accepted QPS COST_Master release, the **machine-generated acceptance receipt is authoritative**. A cryptographically signed Git tag is recommended defense-in-depth but is **not a prerequisite for the first ACCEPTED release** unless an organization-managed signing identity is already commissioned and available on the controlled build machine.

This avoids substituting an ad-hoc personal signing key for the stronger evidence already required by the acceptance gate.

## Required first-release attestation chain

A release may move from `HOLD` to `ACCEPTED` only when the private acceptance receipt binds:

1. CODEX baseline commit;
2. ABACUS baseline commit;
3. accepted SSOT/build version and release ID;
4. immutable local artifact reference;
5. sanitized OneDrive relative publication pointer;
6. Build A/B semantic equality;
7. PASS release receipt;
8. raw SHA-256 for every controlled local artifact;
9. independently calculated raw SHA-256 for every OneDrive publication copy;
10. exact local-to-OneDrive parity;
11. acceptance timestamp and disposition.

The public repository receives only the schema-conformant `qps-cost-master.release-pointer.v1` fields. Confidential evidence, absolute OneDrive paths, per-file private hashes, and local artifact-store internals remain outside public Git.

## Git tag policy

### Current state

`OPTIONAL_DEFENSE_IN_DEPTH`

An annotated or signed tag may be created after a release is accepted, but acceptance does not depend on a tag until signing-key governance is commissioned.

Recommended tag form:

`qps-cost-master/<release-id>`

The tag message should bind the public release pointer file and accepted source commit. It must not contain confidential paths or bidder data.

### Future mandatory-signing gate

Signing can become mandatory only after all of the following are explicitly configured:

- organization-approved signing identity or CI workload identity;
- documented key ownership and rotation/revocation process;
- verification procedure available to future maintainers;
- recovery procedure for lost/rotated credentials;
- branch/tag protection rules that do not make the local build dependent on a single personal device.

When those conditions are met, this policy may be revised to `REQUIRED_SIGNED_TAG` through a governance PR.

## Attestation precedence

If metadata disagrees, use this precedence:

1. raw local/OneDrive SHA-256 parity in the private acceptance receipt;
2. immutable local artifact reference;
3. public release pointer hash fields;
4. source commits recorded in the private receipt;
5. optional Git tag/signature.

A tag never overrides a failed artifact hash, semantic mismatch, failed QA gate, or HOLD disposition.

## Verification after machine loss

A fresh machine must be able to:

1. clone the referenced CODEX and ABACUS commits;
2. bind the verified private evidence registry;
3. rebuild two independent output sets;
4. reproduce semantic equality;
5. compare a candidate build with the accepted release receipt/pointer;
6. verify the immutable OneDrive publication copy without requiring a historical working directory.

This is the governing recovery objective; tag signing is supplementary rather than a substitute for reproducibility.
