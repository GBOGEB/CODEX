# QPS WCS / QRB Energy-Exergy rev1.7 — CODEX roundtrip handoff

## Role split

- **ABACUS owns technical/contract analysis data and the rev1.7 analytical snapshot.**
- **CODEX owns automation, evidence verification, clean-build/fresh-clone receipts, semantic comparison, publication governance and federation handoff.**
- Generated PDF/PPTX/XLSX/HTML are release children, not governing source.
- Confidential/current offer binaries remain outside Git and are represented by filename + SHA-256 + byte size in the evidence registry.

## Current maturity

AMBER. Rev1.7 establishes canonical source inventory, binary manifest, section/deliverable crosswalk, two-sided TP1/TP2 ICD records, equipment/BOM cards, operating scenarios, RFI register, DMAIC metrics and a diagnostic PCA pass.

It must not yet be used as proof that every current-offer section has been extracted, a complete compliance determination, a final bidder comparison, a closed exergy balance, a verified full-price decomposition, evidence of a fresh-clone/CI-CD pass, proof that all uploaded workbooks/PDFs are mutually consistent, or confirmation that no stale references remain.

## Local PC roundtrip

From a clean CODEX clone, with the offer folder as evidence root:

```powershell
$EvidenceRoot = 'C:\Users\gbonthuy\OneDrive - Studiecentrum voor Kernenergie\Master\_Input\OFFERS\_ITT'
$Registry = '.\07_ops\qps_roundtrip\evidence_registry.qps_wcs_qrb_rev1_7.yaml'
$Receipt = '.\runtime\qps-rev1-7\EVIDENCE_VERIFICATION_RECEIPT.json'
$Verified = '.\runtime\qps-rev1-7\evidence_registry.verified.yaml'

.\07_ops\qps_roundtrip\Test-QpsEvidenceRegistry.ps1 `
  -RegistryPath $Registry `
  -EvidenceRoot $EvidenceRoot `
  -ReceiptPath $Receipt `
  -VerifiedRegistryOutput $Verified
```

Then use the existing Wave-2 bootstrap to refresh the clean repositories outside OneDrive and generate repository-state receipts.

## Required release proof before status promotion

1. Evidence registry PASS against the real local binary vault.
2. Clean clones of ABACUS and CODEX outside OneDrive.
3. Build/regeneration from tracked text SSOT and scripts.
4. Recursive manifest verification.
5. Semantic comparison between independent builds.
6. CI status PASS on both integration PRs.
7. Release receipt tied to merged commit SHA.
8. Stale-reference/crosswalk checks PASS.

## Bridge

ABACUS snapshot path: `qplant/energy_exergy/rev1_7/`.
CODEX controlled registry: `07_ops/qps_roundtrip/evidence_registry.qps_wcs_qrb_rev1_7.yaml`.
