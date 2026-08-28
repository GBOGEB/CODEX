# QPS COST_Master release gate status

Status: **HOLD - ACCEPTED RELEASE NOT YET PROVEN**

The public CODEX bridge was integrated by PR #243. That merge closes the repository-integration hold only; it does **not** constitute acceptance of the generated QPS COST_Master release.

## Completed

- CODEX public source-only bridge integrated into `main`.
- Public schemas, bridge contract, roundtrip documentation and source-policy surface established.
- Generated Office/PDF/image/archive artifacts remain outside the public repository.

## Controlling acceptance gate

The accepted-release gate remains closed until a controlled user-PC rebuild produces an accepted release receipt that records all of the following:

1. the CODEX baseline/merge commit used for the rebuild;
2. the ABACUS baseline/merge commit used for the rebuild;
3. the accepted SSOT/build version and release identifier;
4. the accepted local-only artifact Git commit or immutable reference;
5. the OneDrive publication location as a sanitized relative pointer;
6. raw SHA-256 for every controlled outward artifact in the accepted local set;
7. independently calculated raw SHA-256 for every corresponding OneDrive publication copy;
8. exact local-to-OneDrive SHA-256 parity for the complete accepted publication set;
9. acceptance timestamp and disposition.

Until those conditions are satisfied, the release disposition is **HOLD** even though the public bridge is already merged.

## State interpretation

- Repository integration: **COMPLETE**
- Public bridge baseline: **ESTABLISHED**
- PC accepted-release receipt: **PENDING**
- OneDrive raw SHA-256 parity: **PENDING**
- QPS COST_Master accepted-release gate: **HOLD**

Do not place private offer data, the Excel SSOT, generated binaries, raw OneDrive absolute paths, credentials, or the local artifact Git bundle in this repository. When acceptance is achieved, publish only the sanitized version-bound release pointer and hashes permitted by the bridge contract.
