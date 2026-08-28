[CmdletBinding()]
param(
    [string]$RepositoryPath = '.',
    [string]$OutputPath,
    [string[]]$Extensions = @(
        '.xlsx','.xlsm','.xlsb','.docx','.pptx','.pdf',
        '.png','.jpg','.jpeg','.gif','.zip','.tar','.gz','.7z','.rar'
    )
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$ControlledPaths = @(
    '07_ops/qps_roundtrip/',
    'analytics/qps_cost_estimate_roundtrip/',
    'qps_cost_overlay/'
)

Push-Location $RepositoryPath
try {
    $root = (Get-Location).Path
    $tracked = @(git ls-files)
    if ($LASTEXITCODE -ne 0) { throw 'git ls-files failed.' }

    $records = foreach ($relative in $tracked) {
        $normalized = $relative.Replace('\','/')
        $ext = [System.IO.Path]::GetExtension($normalized).ToLowerInvariant()
        if ($Extensions -notcontains $ext) { continue }

        $full = Join-Path $root $relative
        $size = if (Test-Path -LiteralPath $full) { (Get-Item -LiteralPath $full).Length } else { $null }
        $inControlledPath = $false
        foreach ($prefix in $ControlledPaths) {
            if ($normalized.StartsWith($prefix, [System.StringComparison]::OrdinalIgnoreCase)) {
                $inControlledPath = $true
                break
            }
        }

        $classification = if ($inControlledPath) {
            'POLICY_VIOLATION'
        } elseif ($normalized -match '(^|/)(build|dist|output|outputs|render|preview|generated)(/|$)' -or $ext -in @('.png','.jpg','.jpeg','.gif')) {
            'REGENERATE_OR_MIGRATE'
        } else {
            'REVIEW_KEEP_OR_MIGRATE'
        }

        [pscustomobject]@{
            path = $normalized
            extension = $ext
            size_bytes = $size
            classification = $classification
            history_rewrite_required_to_purge = $true
        }
    }

    $records = @($records | Sort-Object path)
    if ($OutputPath) {
        $parent = Split-Path -Parent $OutputPath
        if ($parent -and -not (Test-Path -LiteralPath $parent)) {
            New-Item -ItemType Directory -Path $parent -Force | Out-Null
        }
        $records | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $OutputPath -Encoding utf8
    }

    [ordered]@{
        repository = $root
        tracked_binary_count = $records.Count
        policy_violations = @($records | Where-Object classification -eq 'POLICY_VIOLATION').Count
        regenerate_or_migrate = @($records | Where-Object classification -eq 'REGENERATE_OR_MIGRATE').Count
        review_keep_or_migrate = @($records | Where-Object classification -eq 'REVIEW_KEEP_OR_MIGRATE').Count
        output = $OutputPath
        result = if (@($records | Where-Object classification -eq 'POLICY_VIOLATION').Count -eq 0) { 'PASS' } else { 'FAIL' }
    } | ConvertTo-Json -Depth 4
}
finally {
    Pop-Location
}
