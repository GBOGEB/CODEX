[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [Parameter(Mandatory = $true)][string]$SourceDist,
    [Parameter(Mandatory = $true)][string]$ReleaseId,
    [string]$ReleaseRoot = $env:QPS_RELEASE_ROOT,
    [switch]$CreateOfficeReviewCopy
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Get-RelativeHashMap {
    param([Parameter(Mandatory = $true)][string]$Root)

    $resolved = (Resolve-Path -LiteralPath $Root).Path
    $map = [ordered]@{}
    foreach ($file in Get-ChildItem -LiteralPath $resolved -File -Recurse | Sort-Object FullName) {
        $relative = [System.IO.Path]::GetRelativePath($resolved, $file.FullName).Replace('\', '/')
        if ($relative -eq 'MANIFEST.sha256') {
            continue
        }
        $map[$relative] = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
    }
    return $map
}

if ([string]::IsNullOrWhiteSpace($ReleaseRoot)) {
    throw 'QPS_RELEASE_ROOT is not set and -ReleaseRoot was not provided.'
}
if (-not (Test-Path -LiteralPath $SourceDist)) {
    throw "Source distribution does not exist: $SourceDist"
}

$required = @('BUILD_META.json', 'RELEASE_NOTES.md', 'QA_REPORT.md')
foreach ($name in $required) {
    if (-not (Test-Path -LiteralPath (Join-Path $SourceDist $name))) {
        throw "Required release file is missing: $name"
    }
}

$destination = Join-Path $ReleaseRoot $ReleaseId
if (Test-Path -LiteralPath $destination) {
    throw "Immutable release destination already exists: $destination"
}

if ($PSCmdlet.ShouldProcess($destination, 'Publish immutable QPS release')) {
    New-Item -ItemType Directory -Path $destination -Force | Out-Null
    Copy-Item -LiteralPath (Join-Path $SourceDist '*') -Destination $destination -Recurse -Force

    $sourceHashes = Get-RelativeHashMap -Root $SourceDist
    $destinationHashes = Get-RelativeHashMap -Root $destination

    $differences = @()
    foreach ($key in $sourceHashes.Keys) {
        if (-not $destinationHashes.Contains($key)) {
            $differences += "Missing at destination: $key"
            continue
        }
        if ($sourceHashes[$key] -ne $destinationHashes[$key]) {
            $differences += "Hash mismatch: $key"
        }
    }
    foreach ($key in $destinationHashes.Keys) {
        if (-not $sourceHashes.Contains($key)) {
            $differences += "Unexpected at destination: $key"
        }
    }

    if ($differences.Count -gt 0) {
        throw ("Release verification failed:`n" + ($differences -join "`n"))
    }

    $manifestLines = @(
        '# QPS release SHA-256 manifest'
        "# release_id=$ReleaseId"
        "# generated_utc=$([DateTime]::UtcNow.ToString('o'))"
    )
    $manifestLines += $destinationHashes.GetEnumerator() |
        ForEach-Object { '{0}  {1}' -f $_.Value, $_.Key }
    [System.IO.File]::WriteAllLines(
        (Join-Path $destination 'MANIFEST.sha256'),
        $manifestLines,
        [System.Text.UTF8Encoding]::new($false)
    )

    $reviewDestination = $null
    if ($CreateOfficeReviewCopy) {
        $costRoot = Split-Path -Parent $ReleaseRoot
        $reviewRoot = Join-Path $costRoot '20_WORKING_REVIEW'
        $reviewDestination = Join-Path $reviewRoot $ReleaseId
        if (Test-Path -LiteralPath $reviewDestination) {
            throw "Office review destination already exists: $reviewDestination"
        }
        New-Item -ItemType Directory -Path $reviewDestination -Force | Out-Null
        Copy-Item -LiteralPath (Join-Path $destination '*') -Destination $reviewDestination -Recurse -Force
    }

    [ordered]@{
        release_id = $ReleaseId
        source = (Resolve-Path -LiteralPath $SourceDist).Path
        destination = $destination
        office_review_copy = $reviewDestination
        verified_file_count = $sourceHashes.Count
        result = 'PASS'
    } | ConvertTo-Json -Depth 4
}
