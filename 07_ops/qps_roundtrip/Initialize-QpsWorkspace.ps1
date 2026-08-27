[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [string]$RepoRoot = 'C:\DEV\REPOS',
    [string]$WorkspaceRoot = 'C:\DEV\WORKSPACES\qps-cost',
    [string]$EvidenceRoot = $env:QPS_EVIDENCE_ROOT,
    [string]$ReleaseRoot = $env:QPS_RELEASE_ROOT,
    [switch]$CreateOneDriveFolders
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Ensure-Directory {
    param([Parameter(Mandatory = $true)][string]$Path)

    if (-not (Test-Path -LiteralPath $Path)) {
        if ($PSCmdlet.ShouldProcess($Path, 'Create directory')) {
            New-Item -ItemType Directory -Path $Path -Force | Out-Null
        }
    }
}

$localDirectories = @(
    $RepoRoot,
    $WorkspaceRoot,
    (Join-Path $WorkspaceRoot '_verify'),
    (Join-Path $WorkspaceRoot '_logs')
)

foreach ($directory in $localDirectories) {
    Ensure-Directory -Path $directory
}

if ($CreateOneDriveFolders) {
    if ([string]::IsNullOrWhiteSpace($EvidenceRoot)) {
        throw 'QPS_EVIDENCE_ROOT is not set and -EvidenceRoot was not provided.'
    }
    if ([string]::IsNullOrWhiteSpace($ReleaseRoot)) {
        throw 'QPS_RELEASE_ROOT is not set and -ReleaseRoot was not provided.'
    }

    $costRoot = Split-Path -Parent $ReleaseRoot
    $oneDriveDirectories = @(
        $EvidenceRoot,
        $ReleaseRoot,
        (Join-Path $costRoot '20_WORKING_REVIEW'),
        (Join-Path $costRoot '90_ARCHIVE')
    )

    foreach ($directory in $oneDriveDirectories) {
        Ensure-Directory -Path $directory
    }
}

$summary = [ordered]@{
    repo_root = $RepoRoot
    workspace_root = $WorkspaceRoot
    evidence_root = $EvidenceRoot
    release_root = $ReleaseRoot
    timestamp_utc = [DateTime]::UtcNow.ToString('o')
}

$summary | ConvertTo-Json -Depth 3
