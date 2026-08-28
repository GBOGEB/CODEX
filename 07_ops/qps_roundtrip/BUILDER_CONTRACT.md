# QPS Controlled Builder Contract

Control ID: `GOV-001`

`Invoke-QpsControlledRoundtrip.ps1` deliberately does not embed the QPS cost-model builder. It orchestrates any approved builder that satisfies this interface.

## Required PowerShell parameters

The builder script must accept:

```powershell
param(
    [string]$OutputDirectory,
    [string]$EvidenceRoot,
    [string]$RepoRoot,
    [string]$ReleaseId,
    [string]$BuildLabel
)
```

`BuildLabel` is `A` or `B`. It is provenance only and must not alter engineering content.

## Required outputs

The builder must create these files directly under `OutputDirectory`:

```text
QPS_COST_Master.xlsx
QPS_Cost_Engineering_Handover.docx
QPS_Cost_Management_Deck.pptx
QPS_Cost_Engineering_Handover.pdf
index.html
QA_REPORT.md
RELEASE_NOTES.md
BUILD_META.json
```

The orchestrator generates `semantic/*.semantic.json` and `MANIFEST.sha256` after the builder returns.

## BUILD_META requirements

`BUILD_META.json` must satisfy `Test-QpsReleaseBundle.ps1`, including:

- `schema_version`
- `control_id`
- `release_id`
- `generated_utc`
- `repositories`
- `source_tree_sha256`
- `evidence_registry_sha256`
- `qa.status = PASS`
- `publication.immutable_release = true`
- `publication.office_review_copy = true`

## Determinism rule

Build A and Build B must use the same controlled source commits and verified evidence registry. Volatile timestamps or package metadata may differ, but the extracted semantic manifests must compare equal unless an intentional release change is declared before execution.

## Failure behaviour

The builder must throw or return a non-zero native exit status on failure. It must not silently emit partial release files and report success.

## Boundary

The builder may read confidential evidence from `EvidenceRoot`, but must not copy that evidence into Git. Generated binaries remain in the disposable workspace and the immutable OneDrive release area only.
