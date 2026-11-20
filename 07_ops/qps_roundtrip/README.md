# QPS Roundtrip Governance Tooling

Control ID: GOV-001
Repository role: reusable federation, CI, release, hash and local-workspace tooling.

This directory is deliberately generic. It must not contain QPS bidder values, confidential evidence text or generated deliverables.

## Tools

- `Initialize-QpsWorkspace.ps1`: creates clean local repository, workspace and release roots outside OneDrive.
- `Start-QpsWave2.ps1`: Windows entry point for clean-clone Phase-2 execution.
- `Test-QpsTextOnlyPolicy.ps1`: blocks forbidden binary artifacts in the controlled source path.
- `Get-QpsRecursiveManifest.ps1`: generates recursive SHA-256 manifests for evidence or release trees.
- `Get-QpsSemanticManifest.py`: extracts deterministic meaning-bearing structure from XLSX, DOCX, PPTX and HTML for clean-clone semantic comparison.
- `Get-QpsLegacyBinaryInventory.ps1`: inventories tracked Office/PDF/image/archive binaries without deleting them or rewriting Git history.
- `Test-QpsReleaseBundle.ps1`: validates a release bundle, BUILD_META state and manifest identity before publication.
- `Publish-QpsRelease.ps1`: copies a completed local release to a versioned OneDrive folder and verifies destination hashes.
- `New-QpsReviewChange.ps1`: records normalized Office review changes without treating edited binaries as Git source.

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
  -> generate QA + semantic + exact artifact manifests
  -> compare clean-clone semantic manifests
  -> validate release bundle
  -> publish immutable release
  -> create separate Office review copy
  -> register review changes
  -> assimilate approved changes into text source
```

## Hash separation

Use distinct controls for distinct claims:

1. source/evidence SHA-256 proves which source material was used;
2. semantic SHA-256 compares normalized meaning-bearing output structure across clean builds;
3. artifact SHA-256 protects the exact published binary bytes.

Semantic comparison does not replace formula evaluation, rendering QA or exact release hashes.

## XLSX native feature identity

The XLSX manifest includes `native_feature_contract` version 1. It retains
complete worksheet filter trees, active criteria, sheet visibility, hidden rows
and columns, scoped defined-name attributes and text, explicit calculation
settings and formula attributes. Duplicate scoped names and invalid local-sheet
indices are rejected. A change to these features changes the semantic hash even
when cell values and formula text are unchanged.

Regenerate semantic baselines when adopting this expanded extractor. Formula
caches remain outside deterministic semantic comparison; cache preservation and
recalculation are separate checks. `formula_evaluation = NOT_PERFORMED` is
explicit. No native Excel or contractual-acceptance claim follows from equality.

Run `python -m pytest tests/test_qps_xlsx_native_manifest.py` with the existing
`defusedxml` dependency installed. The production extractor retains that hard
dependency and has no unsafe fallback parser.

## Scope boundary

`CODEX` provides the reusable governance layer only. Canonical QPS analytics remain in `GBOGEB/ABACUS`; project-specific confidential text remains in the private overlay.
