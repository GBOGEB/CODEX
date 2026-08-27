# QPS Roundtrip Governance Tooling

Control ID: GOV-001
Repository role: reusable federation, CI, release, hash and local-workspace tooling.

This directory is deliberately generic. It must not contain QPS bidder values, confidential evidence text or generated deliverables.

## Tools

- `Initialize-QpsWorkspace.ps1`: creates clean local repository, workspace and release roots outside OneDrive.
- `Test-QpsTextOnlyPolicy.ps1`: blocks forbidden binary artifacts in the controlled source path.
- `Get-QpsRecursiveManifest.ps1`: generates recursive SHA-256 manifests for evidence or release trees.
- `Publish-QpsRelease.ps1`: copies a completed local release to a versioned OneDrive folder and verifies destination hashes.

## Required environment variables

```powershell
$env:QPS_EVIDENCE_ROOT = '<OneDriveRoot>\QPS\Cost Estimate\00_EVIDENCE'
$env:QPS_RELEASE_ROOT  = '<OneDriveRoot>\QPS\Cost Estimate\10_RELEASES'
```

Do not hardcode a user profile or OneDrive tenant name in repository source.

## Intended sequence

```text
Initialize workspace
  -> clone/fetch repositories
  -> verify evidence registry
  -> build outside Git working trees
  -> generate QA and manifests
  -> publish immutable release
  -> create separate Office review copy
```

## Scope boundary

`CODEX` provides the reusable governance layer only. Canonical QPS analytics remain in `GBOGEB/ABACUS`; project-specific confidential text remains in the private overlay.
