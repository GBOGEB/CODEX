[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$Root,
    [string]$OutputPath = (Join-Path $Root 'MANIFEST.sha256'),
    [string[]]$ExcludeRelativePaths = @('MANIFEST.sha256')
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$resolvedRoot = (Resolve-Path -LiteralPath $Root).Path
$outputFullPath = [System.IO.Path]::GetFullPath($OutputPath)

$excludeSet = [System.Collections.Generic.HashSet[string]]::new(
    [System.StringComparer]::OrdinalIgnoreCase
)
foreach ($item in $ExcludeRelativePaths) {
    [void]$excludeSet.Add($item.Replace('\', '/'))
}

$records = foreach ($file in Get-ChildItem -LiteralPath $resolvedRoot -File -Recurse | Sort-Object FullName) {
    if ($file.FullName -eq $outputFullPath) {
        continue
    }

    $relative = [System.IO.Path]::GetRelativePath($resolvedRoot, $file.FullName).Replace('\', '/')
    if ($excludeSet.Contains($relative)) {
        continue
    }

    $hash = Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256
    [pscustomobject]@{
        relative_path = $relative
        sha256 = $hash.Hash.ToLowerInvariant()
        size_bytes = $file.Length
    }
}

$parent = Split-Path -Parent $OutputPath
if ($parent -and -not (Test-Path -LiteralPath $parent)) {
    New-Item -ItemType Directory -Path $parent -Force | Out-Null
}

$lines = @(
    '# SHA-256 recursive manifest'
    "# root=$resolvedRoot"
    "# generated_utc=$([DateTime]::UtcNow.ToString('o'))"
)
$lines += $records | ForEach-Object { '{0}  {1}' -f $_.sha256, $_.relative_path }

[System.IO.File]::WriteAllLines($outputFullPath, $lines, [System.Text.UTF8Encoding]::new($false))

[ordered]@{
    root = $resolvedRoot
    output = $outputFullPath
    file_count = @($records).Count
    result = 'PASS'
} | ConvertTo-Json -Depth 3
