[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$LocalDist,
    [Parameter(Mandatory = $true)][string]$PublishedReleaseDirectory,
    [Parameter(Mandatory = $true)][string]$RoundtripReceiptPath,
    [Parameter(Mandatory = $true)][string]$ReleaseReceiptPath,
    [Parameter(Mandatory = $true)][string]$ReleaseId,
    [Parameter(Mandatory = $true)][string]$SsotVersion,
    [Parameter(Mandatory = $true)][string]$CodexCommit,
    [Parameter(Mandatory = $true)][string]$AbacusCommit,
    [Parameter(Mandatory = $true)][string]$LocalArtifactReference,
    [Parameter(Mandatory = $true)][string]$OneDriveRelativePath,
    [string]$OutputPath,
    [string]$BridgePointerOutput
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Assert-Leaf {
    param([Parameter(Mandatory = $true)][string]$Path, [Parameter(Mandatory = $true)][string]$Label)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "$Label not found: $Path"
    }
}

function Assert-Directory {
    param([Parameter(Mandatory = $true)][string]$Path, [Parameter(Mandatory = $true)][string]$Label)
    if (-not (Test-Path -LiteralPath $Path -PathType Container)) {
        throw "$Label not found: $Path"
    }
}

function Read-Json {
    param([Parameter(Mandatory = $true)][string]$Path)
    Assert-Leaf -Path $Path -Label 'JSON receipt'
    return Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json
}

function Get-ManifestMap {
    param([Parameter(Mandatory = $true)][string]$Root)
    $manifest = Join-Path $Root 'MANIFEST.sha256'
    Assert-Leaf -Path $manifest -Label 'Manifest'
    $map = [ordered]@{}
    foreach ($line in Get-Content -LiteralPath $manifest) {
        if (-not $line.Trim() -or $line -match '^#') { continue }
        if ($line -notmatch '^([0-9a-fA-F]{64})\s{2}(.+)$') {
            throw "Malformed manifest line: $line"
        }
        $map[$Matches[2].Replace('\','/')] = $Matches[1].ToLowerInvariant()
    }
    if ($map.Count -eq 0) { throw 'Manifest contains no file records.' }
    return $map
}

function Test-SafeRelativePointer {
    param([Parameter(Mandatory = $true)][string]$Value)
    if ([string]::IsNullOrWhiteSpace($Value)) { return $false }
    if ([System.IO.Path]::IsPathRooted($Value)) { return $false }
    if ($Value -match '^[A-Za-z]:') { return $false }
    if ($Value -match '(^|[\\/])\.\.([\\/]|$)') { return $false }
    return $true
}

Assert-Directory -Path $LocalDist -Label 'Local distribution'
Assert-Directory -Path $PublishedReleaseDirectory -Label 'Published release directory'
if (-not (Test-SafeRelativePointer -Value $OneDriveRelativePath)) {
    throw 'OneDriveRelativePath must be a sanitized relative pointer; absolute paths and parent traversal are forbidden.'
}

$roundtrip = Read-Json -Path $RoundtripReceiptPath
$releaseReceipt = Read-Json -Path $ReleaseReceiptPath

if ($roundtrip.result -ne 'PASS') {
    throw "Roundtrip receipt must be PASS; got '$($roundtrip.result)'."
}
if (-not $roundtrip.all_semantic_comparisons_pass) {
    throw 'Roundtrip receipt does not confirm Build A/B semantic equality.'
}
if ($releaseReceipt.result -ne 'PASS') {
    throw "Release receipt must be PASS; got '$($releaseReceipt.result)'."
}
if ($releaseReceipt.release_id -ne $ReleaseId) {
    throw "Release receipt ID '$($releaseReceipt.release_id)' does not match requested release '$ReleaseId'."
}

$localManifest = Get-ManifestMap -Root $LocalDist
$publishedManifest = Get-ManifestMap -Root $PublishedReleaseDirectory
$allPaths = @($localManifest.Keys + $publishedManifest.Keys | Sort-Object -Unique)
$files = @()
$failures = @()

foreach ($relative in $allPaths) {
    $localFile = Join-Path $LocalDist ($relative.Replace('/', [System.IO.Path]::DirectorySeparatorChar))
    $publishedFile = Join-Path $PublishedReleaseDirectory ($relative.Replace('/', [System.IO.Path]::DirectorySeparatorChar))
    $localExists = Test-Path -LiteralPath $localFile -PathType Leaf
    $publishedExists = Test-Path -LiteralPath $publishedFile -PathType Leaf
    $localHash = if ($localExists) { (Get-FileHash -LiteralPath $localFile -Algorithm SHA256).Hash.ToLowerInvariant() } else { $null }
    $publishedHash = if ($publishedExists) { (Get-FileHash -LiteralPath $publishedFile -Algorithm SHA256).Hash.ToLowerInvariant() } else { $null }
    $manifestLocal = if ($localManifest.Contains($relative)) { $localManifest[$relative] } else { $null }
    $manifestPublished = if ($publishedManifest.Contains($relative)) { $publishedManifest[$relative] } else { $null }

    $status = if (-not $localExists) {
        'MISSING_LOCAL'
    } elseif (-not $publishedExists) {
        'MISSING_PUBLISHED'
    } elseif ($null -eq $manifestLocal) {
        'NOT_IN_LOCAL_MANIFEST'
    } elseif ($null -eq $manifestPublished) {
        'NOT_IN_PUBLISHED_MANIFEST'
    } elseif ($localHash -ne $manifestLocal) {
        'LOCAL_MANIFEST_MISMATCH'
    } elseif ($publishedHash -ne $manifestPublished) {
        'PUBLISHED_MANIFEST_MISMATCH'
    } elseif ($localHash -ne $publishedHash) {
        'LOCAL_ONEDRIVE_HASH_MISMATCH'
    } else {
        'PARITY_VERIFIED'
    }

    if ($status -ne 'PARITY_VERIFIED') { $failures += "$relative: $status" }
    $files += [pscustomobject][ordered]@{
        path = $relative
        local_sha256 = $localHash
        onedrive_sha256 = $publishedHash
        local_manifest_sha256 = $manifestLocal
        onedrive_manifest_sha256 = $manifestPublished
        status = $status
    }
}

$localManifestHash = (Get-FileHash -LiteralPath (Join-Path $LocalDist 'MANIFEST.sha256') -Algorithm SHA256).Hash.ToLowerInvariant()
$publishedManifestHash = (Get-FileHash -LiteralPath (Join-Path $PublishedReleaseDirectory 'MANIFEST.sha256') -Algorithm SHA256).Hash.ToLowerInvariant()
$accepted = ($failures.Count -eq 0 -and $localManifestHash -eq $publishedManifestHash)
if ($localManifestHash -ne $publishedManifestHash) {
    $failures += 'MANIFEST_FILE_HASH_MISMATCH'
    $accepted = $false
}

$acceptance = [ordered]@{
    schema_version = 1
    control_id = 'GOV-001'
    generated_utc = [DateTime]::UtcNow.ToString('o')
    disposition = if ($accepted) { 'ACCEPTED' } else { 'HOLD' }
    release_id = $ReleaseId
    ssot_version = $SsotVersion
    codex_commit = $CodexCommit
    abacus_commit = $AbacusCommit
    local_artifact_reference = $LocalArtifactReference
    onedrive_relative_path = $OneDriveRelativePath.Replace('\','/')
    roundtrip_receipt_result = $roundtrip.result
    semantic_parity = [bool]$roundtrip.all_semantic_comparisons_pass
    release_receipt_result = $releaseReceipt.result
    local_manifest_sha256 = $localManifestHash
    onedrive_manifest_sha256 = $publishedManifestHash
    local_onedrive_manifest_parity = ($localManifestHash -eq $publishedManifestHash)
    file_count = $files.Count
    parity_verified_file_count = @($files | Where-Object status -eq 'PARITY_VERIFIED').Count
    all_artifact_hashes_match = $accepted
    files = $files
    failures = $failures
}

if ([string]::IsNullOrWhiteSpace($OutputPath)) {
    $OutputPath = Join-Path $LocalDist 'ACCEPTANCE_RECEIPT.json'
}
$acceptance | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $OutputPath -Encoding utf8

if ($accepted -and -not [string]::IsNullOrWhiteSpace($BridgePointerOutput)) {
    $pointer = @(
        'schema: qps-cost-master.bridge-pointer.v1',
        "release_id: $ReleaseId",
        "schema_version: 1",
        "private_source_semantic_sha256: $($roundtrip.source_semantic_sha256)",
        'qa_passed: true',
        "qa_total: $($files.Count)",
        "release_manifest_sha256: $localManifestHash",
        "artifact_registry_sha256: $localManifestHash",
        "onedrive_relative_path: $($OneDriveRelativePath.Replace('\','/'))",
        "codex_commit: $CodexCommit",
        "abacus_commit: $AbacusCommit",
        "ssot_version: $SsotVersion",
        "local_artifact_reference: $LocalArtifactReference",
        "accepted_utc: $($acceptance.generated_utc)",
        'disposition: ACCEPTED'
    )
    [System.IO.File]::WriteAllLines($BridgePointerOutput, $pointer, [System.Text.UTF8Encoding]::new($false))
}

$acceptance | ConvertTo-Json -Depth 10
if (-not $accepted) {
    throw ("Accepted-release parity gate remains HOLD:`n" + ($failures -join "`n"))
}
