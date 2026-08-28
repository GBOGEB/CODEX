[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$ReleaseDirectory,
    [Parameter(Mandatory = $true)][string]$ReleaseId,
    [Parameter(Mandatory = $true)][string]$SourceCommit,
    [string]$ReceiptPath,
    [string]$ManifestName = 'MANIFEST.sha256',
    [string]$BuildMetaName = 'BUILD_META.json'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if (-not (Test-Path -LiteralPath $ReleaseDirectory -PathType Container)) {
    throw "Release directory not found: $ReleaseDirectory"
}
$resolved = (Resolve-Path -LiteralPath $ReleaseDirectory).Path
$manifestPath = Join-Path $resolved $ManifestName
$buildMetaPath = Join-Path $resolved $BuildMetaName

if (-not (Test-Path -LiteralPath $manifestPath -PathType Leaf)) {
    throw "Release manifest missing: $manifestPath"
}
if (-not (Test-Path -LiteralPath $buildMetaPath -PathType Leaf)) {
    throw "Build metadata missing: $buildMetaPath"
}

$buildMeta = Get-Content -LiteralPath $buildMetaPath -Raw | ConvertFrom-Json
if ($buildMeta.qa.status -ne 'PASS') {
    throw "BUILD_META QA status must be PASS; got '$($buildMeta.qa.status)'."
}

$manifestHash = (Get-FileHash -LiteralPath $manifestPath -Algorithm SHA256).Hash.ToLowerInvariant()
$entries = @()
$failures = @()
foreach ($line in Get-Content -LiteralPath $manifestPath) {
    if (-not $line.Trim() -or $line -match '^#') { continue }
    if ($line -notmatch '^([0-9a-fA-F]{64})\s{2}(.+)$') {
        $failures += "Malformed manifest line: $line"
        continue
    }
    $expected = $Matches[1].ToLowerInvariant()
    $relative = $Matches[2]
    $filePath = Join-Path $resolved ($relative.Replace('/', [System.IO.Path]::DirectorySeparatorChar))
    if (-not (Test-Path -LiteralPath $filePath -PathType Leaf)) {
        $failures += "Missing release file: $relative"
        $entries += [pscustomobject]@{ path = $relative; expected_sha256 = $expected; actual_sha256 = $null; status = 'MISSING' }
        continue
    }
    $actual = (Get-FileHash -LiteralPath $filePath -Algorithm SHA256).Hash.ToLowerInvariant()
    $status = if ($actual -eq $expected) { 'VERIFIED' } else { 'HASH_MISMATCH' }
    if ($status -ne 'VERIFIED') { $failures += "${relative}: $status" }
    $entries += [pscustomobject]@{ path = $relative; expected_sha256 = $expected; actual_sha256 = $actual; status = $status }
}

$receipt = [ordered]@{
    schema_version = 1
    control_id = 'GOV-001'
    generated_utc = [DateTime]::UtcNow.ToString('o')
    release_id = $ReleaseId
    source_commit = $SourceCommit
    release_directory = $resolved
    manifest_sha256 = $manifestHash
    build_meta_qa_status = $buildMeta.qa.status
    verified_file_count = @($entries | Where-Object { $_.status -eq 'VERIFIED' }).Count
    file_count = $entries.Count
    all_manifest_entries_verified = ($failures.Count -eq 0)
    files = $entries
    result = if ($failures.Count -eq 0) { 'PASS' } else { 'FAIL' }
}

if ([string]::IsNullOrWhiteSpace($ReceiptPath)) {
    $ReceiptPath = Join-Path $resolved 'RELEASE_RECEIPT.json'
}
$receipt | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $ReceiptPath -Encoding utf8
$receipt | ConvertTo-Json -Depth 8

if ($failures.Count -gt 0) {
    throw ("Release receipt verification failed:`n" + ($failures -join "`n"))
}
