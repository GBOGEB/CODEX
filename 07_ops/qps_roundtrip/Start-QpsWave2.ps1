[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [string]$RepoRoot = 'C:\DEV\REPOS',
    [string]$WorkspaceRoot = 'C:\DEV\WORKSPACES\qps-cost',
    [Parameter(Mandatory = $true)][string]$EvidenceRoot,
    [Parameter(Mandatory = $true)][string]$ReleaseRoot,
    [switch]$SkipClone,
    [switch]$CreateOneDriveFolders
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$repositories = @(
    [pscustomobject]@{ Name = 'ABACUS'; Url = 'https://github.com/GBOGEB/ABACUS.git' },
    [pscustomobject]@{ Name = 'CODEX'; Url = 'https://github.com/GBOGEB/CODEX.git' },
    [pscustomobject]@{ Name = 'cryoplant-project'; Url = 'https://github.com/GBOGEB/cryoplant-project.git' },
    [pscustomobject]@{ Name = 'DOCX_RTM_Automation'; Url = 'https://github.com/GBOGEB/DOCX_RTM_Automation.git' }
)

function Assert-Command {
    param([Parameter(Mandatory = $true)][string]$Name)
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "Required command is not available: $Name"
    }
}

function Assert-CleanRepository {
    param([Parameter(Mandatory = $true)][string]$Path)

    $status = @(git -C $Path status --porcelain)
    if ($LASTEXITCODE -ne 0) {
        throw "Unable to read Git status: $Path"
    }
    if ($status.Count -gt 0) {
        throw "Repository has local changes and will not be updated automatically: $Path"
    }
}

Assert-Command -Name 'git'

if (-not (Test-Path -LiteralPath $RepoRoot)) {
    if ($PSCmdlet.ShouldProcess($RepoRoot, 'Create repository root')) {
        New-Item -ItemType Directory -Path $RepoRoot -Force | Out-Null
    }
}

if (-not $SkipClone) {
    foreach ($repo in $repositories) {
        $path = Join-Path $RepoRoot $repo.Name
        if (-not (Test-Path -LiteralPath $path)) {
            if ($PSCmdlet.ShouldProcess($path, "Clone $($repo.Url)")) {
                git clone $repo.Url $path
                if ($LASTEXITCODE -ne 0) { throw "Clone failed: $($repo.Name)" }
            }
        } else {
            if (-not (Test-Path -LiteralPath (Join-Path $path '.git'))) {
                throw "Existing path is not a Git clone: $path"
            }
            Assert-CleanRepository -Path $path
            if ($PSCmdlet.ShouldProcess($path, 'Fetch and fast-forward default branch')) {
                git -C $path fetch --all --prune
                if ($LASTEXITCODE -ne 0) { throw "Fetch failed: $($repo.Name)" }
                $defaultBranch = (git -C $path symbolic-ref refs/remotes/origin/HEAD).Trim() -replace '^refs/remotes/origin/', ''
                if ([string]::IsNullOrWhiteSpace($defaultBranch)) { throw "Unable to determine default branch: $($repo.Name)" }
                git -C $path switch $defaultBranch
                if ($LASTEXITCODE -ne 0) { throw "Switch failed: $($repo.Name)" }
                git -C $path pull --ff-only
                if ($LASTEXITCODE -ne 0) { throw "Fast-forward pull failed: $($repo.Name)" }
            }
        }
    }
}

$env:QPS_EVIDENCE_ROOT = $EvidenceRoot
$env:QPS_RELEASE_ROOT = $ReleaseRoot

$initializer = Join-Path $RepoRoot 'CODEX\07_ops\qps_roundtrip\Initialize-QpsWorkspace.ps1'
if (-not (Test-Path -LiteralPath $initializer)) {
    throw "QPS workspace initializer not found. Ensure the CODEX Wave 1 tooling is merged/present: $initializer"
}

$initArgs = @{
    RepoRoot = $RepoRoot
    WorkspaceRoot = $WorkspaceRoot
    EvidenceRoot = $EvidenceRoot
    ReleaseRoot = $ReleaseRoot
}
if ($CreateOneDriveFolders) { $initArgs.CreateOneDriveFolders = $true }

& $initializer @initArgs | Write-Host

$repoState = foreach ($repo in $repositories) {
    $path = Join-Path $RepoRoot $repo.Name
    if (Test-Path -LiteralPath (Join-Path $path '.git')) {
        [pscustomobject]@{
            repository = $repo.Name
            path = $path
            branch = (git -C $path branch --show-current).Trim()
            commit = (git -C $path rev-parse HEAD).Trim()
            clean = (@(git -C $path status --porcelain).Count -eq 0)
        }
    }
}

[ordered]@{
    phase = 'W002-bootstrap'
    repo_root = $RepoRoot
    workspace_root = $WorkspaceRoot
    evidence_root = $EvidenceRoot
    release_root = $ReleaseRoot
    repositories = @($repoState)
    timestamp_utc = [DateTime]::UtcNow.ToString('o')
    result = 'READY_FOR_EVIDENCE_BINDING'
} | ConvertTo-Json -Depth 5
