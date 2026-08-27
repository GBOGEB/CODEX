[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$DistPath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if (-not (Test-Path -LiteralPath $DistPath)) {
    throw "Release bundle does not exist: $DistPath"
}

$required = @(
    'QPS_COST_Master.xlsx',
    'QPS_Cost_Engineering_Handover.docx',
    'QPS_Cost_Management_Deck.pptx',
    'QPS_Cost_Engineering_Handover.pdf',
    'index.html',
    'QA_REPORT.md',
    'RELEASE_NOTES.md',
    'BUILD_META.json',
    'MANIFEST.sha256'
)

$missing = @()
foreach ($name in $required) {
    if (-not (Test-Path -LiteralPath (Join-Path $DistPath $name))) {
        $missing += $name
    }
}
if ($missing.Count -gt 0) {
    throw ("Missing required release files:`n" + ($missing -join "`n"))
}

$metaPath = Join-Path $DistPath 'BUILD_META.json'
try {
    $meta = Get-Content -LiteralPath $metaPath -Raw | ConvertFrom-Json
}
catch {
    throw "BUILD_META.json is not valid JSON: $($_.Exception.Message)"
}

$requiredMeta = @(
    'schema_version',
    'control_id',
    'release_id',
    'generated_utc',
    'repositories',
    'source_tree_sha256',
    'evidence_registry_sha256',
    'qa',
    'publication'
)
$missingMeta = @()
foreach ($field in $requiredMeta) {
    if (-not ($meta.PSObject.Properties.Name -contains $field)) {
        $missingMeta += $field
    }
}
if ($missingMeta.Count -gt 0) {
    throw ("BUILD_META.json missing fields:`n" + ($missingMeta -join "`n"))
}

if ($meta.qa.status -ne 'PASS') {
    throw "QA status must be PASS before publication. Current: $($meta.qa.status)"
}
if (-not $meta.publication.immutable_release) {
    throw 'BUILD_META publication.immutable_release must be true.'
}
if (-not $meta.publication.office_review_copy) {
    throw 'BUILD_META publication.office_review_copy must be true.'
}

$manifestPath = Join-Path $DistPath 'MANIFEST.sha256'
$manifestLines = Get-Content -LiteralPath $manifestPath |
    Where-Object { $_ -and -not $_.StartsWith('#') }
if ($manifestLines.Count -eq 0) {
    throw 'MANIFEST.sha256 contains no artifact records.'
}

$manifestMap = @{}
foreach ($line in $manifestLines) {
    if ($line -notmatch '^([0-9a-fA-F]{64})\s\s(.+)$') {
        throw "Invalid manifest line: $line"
    }
    $manifestMap[$Matches[2].Replace('\','/')] = $Matches[1].ToLowerInvariant()
}

$mismatches = @()
foreach ($entry in $manifestMap.GetEnumerator()) {
    $path = Join-Path $DistPath $entry.Key
    if (-not (Test-Path -LiteralPath $path)) {
        $mismatches += "Missing file referenced by manifest: $($entry.Key)"
        continue
    }
    $actual = (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($actual -ne $entry.Value) {
        $mismatches += "Hash mismatch: $($entry.Key)"
    }
}
if ($mismatches.Count -gt 0) {
    throw ("Release manifest verification failed:`n" + ($mismatches -join "`n"))
}

[ordered]@{
    result = 'PASS'
    release_id = $meta.release_id
    required_files = $required.Count
    manifest_records = $manifestMap.Count
    qa_status = $meta.qa.status
    immutable_release = [bool]$meta.publication.immutable_release
    office_review_copy = [bool]$meta.publication.office_review_copy
} | ConvertTo-Json -Depth 4
