[CmdletBinding()]
param(
    [string]$RepositoryPath = '.',
    [string[]]$ControlledPaths = @(
        'analytics/qps_cost_estimate_roundtrip/',
        '07_ops/qps_roundtrip/',
        'qps_cost_overlay/'
    ),
    [string[]]$FileList,
    [switch]$IncludeUntracked
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$forbiddenPattern = '\.(xlsx|xlsm|xlsb|docx|pptx|pdf|png|jpg|jpeg|gif|zip|tar|gz|7z|rar)$'
$temporaryPattern = '(^|/)(~\$|\.DS_Store$)|\.(tmp|bak|swp)$'

Push-Location $RepositoryPath
try {
    if (-not $FileList) {
        $FileList = @(git diff --cached --name-only --diff-filter=ACMR)
        if ($LASTEXITCODE -ne 0) {
            throw 'Unable to read staged Git file list.'
        }

        if ($IncludeUntracked) {
            $FileList += @(git ls-files --others --exclude-standard)
            if ($LASTEXITCODE -ne 0) {
                throw 'Unable to read untracked Git file list.'
            }
        }
    }

    $normalized = $FileList |
        Where-Object { -not [string]::IsNullOrWhiteSpace($_) } |
        ForEach-Object { $_.Replace('\', '/') } |
        Sort-Object -Unique

    $controlled = foreach ($file in $normalized) {
        foreach ($prefix in $ControlledPaths) {
            if ($file.StartsWith($prefix.Replace('\', '/'), [System.StringComparison]::OrdinalIgnoreCase)) {
                $file
                break
            }
        }
    }

    $blocked = @($controlled | Where-Object {
        ($_ -match $forbiddenPattern) -or ($_ -match $temporaryPattern)
    })

    if ($blocked.Count -gt 0) {
        Write-Error ("QPS text-only policy failed. Remove these files from Git:`n" + ($blocked -join "`n"))
        exit 1
    }

    [ordered]@{
        policy = 'QPS text-only controlled paths'
        checked_files = @($controlled).Count
        blocked_files = 0
        result = 'PASS'
    } | ConvertTo-Json -Depth 3
}
finally {
    Pop-Location
}
