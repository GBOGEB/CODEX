[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$RegistryPath,
    [string]$EvidenceRoot = $env:QPS_EVIDENCE_ROOT,
    [string]$ReceiptPath,
    [string]$VerifiedRegistryOutput
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$trimChars = [char[]]@(' ', "'", '"')

if ([string]::IsNullOrWhiteSpace($EvidenceRoot)) {
    throw 'QPS_EVIDENCE_ROOT is not set and -EvidenceRoot was not supplied.'
}
if (-not (Test-Path -LiteralPath $RegistryPath)) {
    throw "Evidence registry not found: $RegistryPath"
}
if (-not (Test-Path -LiteralPath $EvidenceRoot -PathType Container)) {
    throw "Evidence root not found: $EvidenceRoot"
}

$lines = @(Get-Content -LiteralPath $RegistryPath)
$records = @()
$current = $null

function Complete-Record {
    param($Record)

    if ($null -ne $Record -and $Record.Contains('id')) {
        $script:records += [pscustomobject]$Record
    }
}

foreach ($line in $lines) {
    if ($line -match '^\s*- id:\s*(.+?)\s*$') {
        Complete-Record $current
        $current = [ordered]@{
            id = $Matches[1].Trim($trimChars)
        }
        continue
    }
    if ($null -eq $current) {
        continue
    }

    if ($line -match '^\s+required:\s*(true|false)\s*$') {
        $current.required = [bool]::Parse($Matches[1])
    }
    elseif ($line -match '^\s+expected_filename:\s*(.+?)\s*$') {
        $current.expected_filename = $Matches[1].Trim($trimChars)
    }
    elseif ($line -match '^\s+relative_path:\s*(.+?)\s*$') {
        $current.relative_path = $Matches[1].Trim($trimChars)
    }
    elseif ($line -match '^\s+sha256:\s*([0-9a-fA-F]{64})\s*$') {
        $current.sha256 = $Matches[1].ToLowerInvariant()
    }
    elseif ($line -match '^\s+size_bytes:\s*(null|\d+)\s*$') {
        $current.size_bytes = if ($Matches[1] -eq 'null') {
            $null
        }
        else {
            [int64]$Matches[1]
        }
    }
    elseif ($line -match '^\s+verification_status:\s*(.+?)\s*$') {
        $current.verification_status = $Matches[1].Trim($trimChars)
    }
}
Complete-Record $current

if ($records.Count -eq 0) {
    throw 'No evidence records were parsed from the registry.'
}

$results = @()
$failures = @()
foreach ($record in $records) {
    $relative = $record.relative_path.Replace(
        '/',
        [System.IO.Path]::DirectorySeparatorChar
    )
    $fullPath = Join-Path $EvidenceRoot $relative
    $exists = Test-Path -LiteralPath $fullPath -PathType Leaf

    $actualSize = $null
    $actualHash = $null
    $nameMatches = $false
    $hashMatches = $false
    $sizeMatches = $false

    if ($exists) {
        $item = Get-Item -LiteralPath $fullPath
        $actualSize = [int64]$item.Length
        $actualHash = (
            Get-FileHash -LiteralPath $fullPath -Algorithm SHA256
        ).Hash.ToLowerInvariant()
        $nameMatches = ($item.Name -eq $record.expected_filename)
        $hashMatches = ($actualHash -eq $record.sha256)
        $sizeMatches = (
            $null -eq $record.size_bytes -or
            $actualSize -eq [int64]$record.size_bytes
        )
    }

    $status = if (-not $exists) {
        'MISSING'
    }
    elseif (-not $nameMatches) {
        'FILENAME_MISMATCH'
    }
    elseif (-not $hashMatches) {
        'HASH_MISMATCH'
    }
    elseif (-not $sizeMatches) {
        'SIZE_MISMATCH'
    }
    else {
        'VERIFIED'
    }

    if ($record.required -and $status -ne 'VERIFIED') {
        $failures += "$($record.id): $status"
    }

    $results += [pscustomobject][ordered]@{
        id = $record.id
        required = $record.required
        relative_path = $record.relative_path
        expected_filename = $record.expected_filename
        exists = $exists
        expected_sha256 = $record.sha256
        actual_sha256 = $actualHash
        expected_size_bytes = $record.size_bytes
        actual_size_bytes = $actualSize
        status = $status
    }
}

$allRequiredVerified = ($failures.Count -eq 0)
$receipt = [ordered]@{
    schema_version = 1
    control_id = 'GOV-001'
    generated_utc = [DateTime]::UtcNow.ToString('o')
    registry_path = (Resolve-Path -LiteralPath $RegistryPath).Path
    evidence_root = (Resolve-Path -LiteralPath $EvidenceRoot).Path
    required_count = @(
        $results | Where-Object { $_.required }
    ).Count
    verified_required_count = @(
        $results | Where-Object {
            $_.required -and $_.status -eq 'VERIFIED'
        }
    ).Count
    all_required_verified = $allRequiredVerified
    evidence = $results
    result = if ($allRequiredVerified) { 'PASS' } else { 'FAIL' }
}

if ([string]::IsNullOrWhiteSpace($ReceiptPath)) {
    $ReceiptPath = Join-Path (
        Get-Location
    ) 'EVIDENCE_VERIFICATION_RECEIPT.json'
}
$receipt |
    ConvertTo-Json -Depth 8 |
    Set-Content -LiteralPath $ReceiptPath -Encoding utf8

if (
    $allRequiredVerified -and
    -not [string]::IsNullOrWhiteSpace($VerifiedRegistryOutput)
) {
    $updated = [System.Collections.Generic.List[string]]::new()
    $recordById = @{}
    foreach ($r in $results) {
        $recordById[$r.id] = $r
    }
    $activeId = $null

    foreach ($line in $lines) {
        if ($line -match '^registry_status:\s*.*$') {
            $updated.Add('registry_status: VERIFIED')
            continue
        }
        if ($line -match '^build_blocking:\s*.*$') {
            $updated.Add('build_blocking: false')
            continue
        }
        if ($line -match '^\s*- id:\s*(.+?)\s*$') {
            $activeId = $Matches[1].Trim($trimChars)
            $updated.Add($line)
            continue
        }
        if ($activeId -and $recordById.ContainsKey($activeId)) {
            if ($line -match '^\s+size_bytes:\s*.*$') {
                $indent = ($line -replace '^(\s*).*$', '$1')
                $updated.Add(
                    "${indent}size_bytes: " +
                    $recordById[$activeId].actual_size_bytes
                )
                continue
            }
            if ($line -match '^\s+verification_status:\s*.*$') {
                $indent = ($line -replace '^(\s*).*$', '$1')
                $updated.Add(
                    "${indent}verification_status: VERIFIED"
                )
                continue
            }
        }
        $updated.Add($line)
    }
    [System.IO.File]::WriteAllLines(
        $VerifiedRegistryOutput,
        $updated,
        [System.Text.UTF8Encoding]::new($false)
    )
}

$receipt | ConvertTo-Json -Depth 8
if (-not $allRequiredVerified) {
    throw (
        "Evidence verification failed:`n" +
        ($failures -join "`n")
    )
}
