[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [string]$RepoRoot = 'C:\DEV\REPOS',
    [string]$WorkspaceRoot = 'C:\DEV\WORKSPACES\qps-cost',
    [Parameter(Mandatory = $true)][string]$EvidenceRoot,
    [Parameter(Mandatory = $true)][string]$ReleaseRoot,
    [Parameter(Mandatory = $true)][string]$ReleaseId,
    [Parameter(Mandatory = $true)][string]$BuilderScript,
    [string]$RegistryPath,
    [switch]$Publish,
    [switch]$CreateOneDriveFolders,
    [switch]$SkipRepositoryUpdate
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Assert-Leaf {
    param([Parameter(Mandatory = $true)][string]$Path, [Parameter(Mandatory = $true)][string]$Label)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "$Label not found: $Path"
    }
}

function Get-Sha256Text {
    param([Parameter(Mandatory = $true)][string]$Text)
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try {
        $bytes = [System.Text.Encoding]::UTF8.GetBytes($Text)
        return ([System.BitConverter]::ToString($sha.ComputeHash($bytes))).Replace('-', '').ToLowerInvariant()
    }
    finally {
        $sha.Dispose()
    }
}

$toolRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$startWave2 = Join-Path $toolRoot 'Start-QpsWave2.ps1'
$verifyEvidence = Join-Path $toolRoot 'Test-QpsEvidenceRegistry.ps1'
$semanticExtractor = Join-Path $toolRoot 'Get-QpsSemanticManifest.py'
$semanticCompare = Join-Path $toolRoot 'Compare-QpsSemanticManifests.py'
$getManifest = Join-Path $toolRoot 'Get-QpsRecursiveManifest.ps1'
$testBundle = Join-Path $toolRoot 'Test-QpsReleaseBundle.ps1'
$publisher = Join-Path $toolRoot 'Publish-QpsRelease.ps1'
$releaseReceiptTool = Join-Path $toolRoot 'New-QpsReleaseReceipt.ps1'

foreach ($tool in @($startWave2, $verifyEvidence, $semanticExtractor, $semanticCompare, $getManifest, $testBundle, $publisher, $releaseReceiptTool)) {
    Assert-Leaf -Path $tool -Label 'Required QPS roundtrip tool'
}
Assert-Leaf -Path $BuilderScript -Label 'Builder script'

if ([string]::IsNullOrWhiteSpace($RegistryPath)) {
    $RegistryPath = Join-Path $RepoRoot 'cryoplant-project\qps_cost_overlay\evidence_registry.yaml'
}
Assert-Leaf -Path $RegistryPath -Label 'Evidence registry'

$bootstrapArgs = @{
    RepoRoot = $RepoRoot
    WorkspaceRoot = $WorkspaceRoot
    EvidenceRoot = $EvidenceRoot
    ReleaseRoot = $ReleaseRoot
}
if ($CreateOneDriveFolders) { $bootstrapArgs.CreateOneDriveFolders = $true }
if ($SkipRepositoryUpdate) { $bootstrapArgs.SkipClone = $true }
$bootstrap = & $startWave2 @bootstrapArgs | ConvertFrom-Json

$runRoot = Join-Path $WorkspaceRoot $ReleaseId
if (Test-Path -LiteralPath $runRoot) {
    throw "Roundtrip workspace already exists; release IDs are immutable per run: $runRoot"
}
New-Item -ItemType Directory -Force $runRoot | Out-Null
$receiptsRoot = Join-Path $runRoot 'receipts'
$comparisonRoot = Join-Path $runRoot 'semantic-comparison'
New-Item -ItemType Directory -Force $receiptsRoot, $comparisonRoot | Out-Null

$evidenceReceiptPath = Join-Path $receiptsRoot 'EVIDENCE_VERIFICATION_RECEIPT.json'
$verifiedRegistryPath = Join-Path $receiptsRoot 'evidence_registry.verified.yaml'
$evidence = & $verifyEvidence `
    -RegistryPath $RegistryPath `
    -EvidenceRoot $EvidenceRoot `
    -ReceiptPath $evidenceReceiptPath `
    -VerifiedRegistryOutput $verifiedRegistryPath | ConvertFrom-Json
if ($evidence.result -ne 'PASS') { throw 'Evidence verification did not return PASS.' }

$builds = @()
foreach ($label in @('A', 'B')) {
    $buildRoot = Join-Path $runRoot "build-$label"
    $dist = Join-Path $buildRoot 'dist'
    New-Item -ItemType Directory -Force $dist | Out-Null

    & $BuilderScript `
        -OutputDirectory $dist `
        -EvidenceRoot $EvidenceRoot `
        -RepoRoot $RepoRoot `
        -ReleaseId $ReleaseId `
        -BuildLabel $label
    if ($LASTEXITCODE -and $LASTEXITCODE -ne 0) {
        throw "Builder returned exit code $LASTEXITCODE for build $label."
    }

    $semanticDir = Join-Path $dist 'semantic'
    New-Item -ItemType Directory -Force $semanticDir | Out-Null
    $semanticArtifacts = @(
        'QPS_COST_Master.xlsx',
        'QPS_Cost_Engineering_Handover.docx',
        'QPS_Cost_Management_Deck.pptx',
        'index.html'
    )
    $semanticFiles = @()
    foreach ($artifactName in $semanticArtifacts) {
        $artifact = Join-Path $dist $artifactName
        Assert-Leaf -Path $artifact -Label "Build $label semantic artifact"
        $semanticName = ([System.IO.Path]::GetFileNameWithoutExtension($artifactName) + '.semantic.json')
        $semanticPath = Join-Path $semanticDir $semanticName
        python $semanticExtractor $artifact -o $semanticPath
        if ($LASTEXITCODE -ne 0) { throw "Semantic extraction failed for build $($label): $artifactName" }
        $semanticFiles += $semanticPath
    }

    $manifestPath = Join-Path $dist 'MANIFEST.sha256'
    if (Test-Path -LiteralPath $manifestPath) { Remove-Item -LiteralPath $manifestPath -Force }
    & $getManifest -Root $dist | Write-Host
    $bundle = & $testBundle -DistPath $dist | ConvertFrom-Json
    if ($bundle.result -ne 'PASS') { throw "Release bundle validation failed for build $label." }

    $builds += [pscustomobject]@{
        label = $label
        build_root = $buildRoot
        dist = $dist
        semantic_dir = $semanticDir
        semantic_files = $semanticFiles
        bundle = $bundle
    }
}

$comparisons = @()
$semanticNames = @(
    'QPS_COST_Master.semantic.json',
    'QPS_Cost_Engineering_Handover.semantic.json',
    'QPS_Cost_Management_Deck.semantic.json',
    'index.semantic.json'
)
foreach ($name in $semanticNames) {
    $a = Join-Path $builds[0].semantic_dir $name
    $b = Join-Path $builds[1].semantic_dir $name
    $receipt = Join-Path $comparisonRoot ($name -replace '\.semantic\.json$', '.comparison.json')
    python $semanticCompare $a $b --output $receipt | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "Semantic comparison failed for $name" }
    $comparisons += (Get-Content -LiteralPath $receipt -Raw | ConvertFrom-Json)
}

$semanticSetLines = foreach ($name in $semanticNames | Sort-Object) {
    $manifest = Get-Content -LiteralPath (Join-Path $builds[0].semantic_dir $name) -Raw | ConvertFrom-Json
    if (-not $manifest.semantic_sha256) { throw "Semantic manifest is missing semantic_sha256: $name" }
    "$name=$($manifest.semantic_sha256)"
}
$privateSourceSemanticSha256 = Get-Sha256Text -Text ($semanticSetLines -join "`n")

$sourceCommit = ''
$codexPath = Join-Path $RepoRoot 'CODEX'
if (Test-Path -LiteralPath (Join-Path $codexPath '.git')) {
    $sourceCommit = (git -C $codexPath rev-parse HEAD).Trim()
}

$publication = $null
$releaseReceipt = $null
if ($Publish) {
    if ([string]::IsNullOrWhiteSpace($sourceCommit)) {
        throw 'Cannot publish without resolving the CODEX source commit.'
    }
    if ($PSCmdlet.ShouldProcess((Join-Path $ReleaseRoot $ReleaseId), 'Publish immutable QPS release')) {
        $publication = & $publisher `
            -SourceDist $builds[0].dist `
            -ReleaseId $ReleaseId `
            -ReleaseRoot $ReleaseRoot `
            -CreateOfficeReviewCopy | ConvertFrom-Json
        if ($publication.result -ne 'PASS') { throw 'Publication did not return PASS.' }

        $releaseReceiptPath = Join-Path $receiptsRoot 'RELEASE_RECEIPT.json'
        $releaseReceipt = & $releaseReceiptTool `
            -ReleaseDirectory $publication.destination `
            -ReleaseId $ReleaseId `
            -SourceCommit $sourceCommit `
            -ReceiptPath $releaseReceiptPath | ConvertFrom-Json
        if ($releaseReceipt.result -ne 'PASS') { throw 'Release receipt did not return PASS.' }
    }
}

$roundtripReceipt = [ordered]@{
    schema_version = 1
    control_id = 'GOV-001'
    generated_utc = [DateTime]::UtcNow.ToString('o')
    release_id = $ReleaseId
    source_commit = $sourceCommit
    private_source_semantic_sha256 = $privateSourceSemanticSha256
    bootstrap_result = $bootstrap.result
    evidence_result = $evidence.result
    evidence_receipt = $evidenceReceiptPath
    verified_registry_candidate = $verifiedRegistryPath
    build_a = $builds[0].dist
    build_b = $builds[1].dist
    semantic_comparison_count = $comparisons.Count
    all_semantic_comparisons_pass = (@($comparisons | Where-Object { $_.result -ne 'PASS' }).Count -eq 0)
    published = [bool]$Publish
    publication_destination = if ($publication) { $publication.destination } else { $null }
    office_review_copy = if ($publication) { $publication.office_review_copy } else { $null }
    release_receipt_result = if ($releaseReceipt) { $releaseReceipt.result } else { $null }
    result = 'PASS'
}
$roundtripReceiptPath = Join-Path $receiptsRoot 'ROUNDTRIP_RECEIPT.json'
$roundtripReceipt | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $roundtripReceiptPath -Encoding utf8
$roundtripReceipt | ConvertTo-Json -Depth 8
