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
    [pscustomobject]@{
        Name = 'ABACUS'
        Url = 'https://github.com/GBOGEB/ABACUS.git'
    },
    [pscustomobject]@{
        Name = 'CODEX'
        Url = 'https://github.com/GBOGEB/CODEX.git'
    },
    [pscustomobject]@{
        Name = 'cryoplant-project'
        Url = 'https://github.com/GBOGEB/cryoplant-project.git'
    },
    [pscustomobject]@{
        Name = 'DOCX_RTM_Automation'
        Url = 'https://github.com/GBOGEB/DOCX_RTM_Automation.git'
    }
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
        throw "Repository has local changes: $Path"
    }
}

function Normalize-GitRemote {
    param([Parameter(Mandatory = $true)][string]$Remote)

    $value = $Remote.Trim().TrimEnd('/')
    $value = $value -replace '\.git$', ''
    $value = $value -replace '^git@github\.com:', 'https://github.com/'
    $value.ToLowerInvariant()
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
                if ($LASTEXITCODE -ne 0) {
                    throw "Clone failed: $($repo.Name)"
                }
            }
        }
        else {
            if (-not (Test-Path -LiteralPath (Join-Path $path '.git'))) {
                throw "Existing path is not a Git clone: $path"
            }
            Assert-CleanRepository -Path $path
            if ($PSCmdlet.ShouldProcess(
                    $path,
                    'Fetch and fast-forward default branch')) {
                git -C $path fetch --all --prune
                if ($LASTEXITCODE -ne 0) {
                    throw "Fetch failed: $($repo.Name)"
                }
                $defaultBranch = (
                    git -C $path symbolic-ref refs/remotes/origin/HEAD
                ).Trim() -replace '^refs/remotes/origin/', ''
                if ([string]::IsNullOrWhiteSpace($defaultBranch)) {
                    throw "Unable to determine default branch: $($repo.Name)"
                }
                git -C $path switch $defaultBranch
                if ($LASTEXITCODE -ne 0) {
                    throw "Switch failed: $($repo.Name)"
                }
                git -C $path pull --ff-only
                if ($LASTEXITCODE -ne 0) {
                    throw "Fast-forward pull failed: $($repo.Name)"
                }
            }
        }
    }
}

$env:QPS_EVIDENCE_ROOT = $EvidenceRoot
$env:QPS_RELEASE_ROOT = $ReleaseRoot

$initializer = Join-Path `
    $RepoRoot `
    'CODEX\07_ops\qps_roundtrip\Initialize-QpsWorkspace.ps1'
if (-not (Test-Path -LiteralPath $initializer)) {
    throw "QPS workspace initializer not found: $initializer"
}

$initArgs = @{
    RepoRoot = $RepoRoot
    WorkspaceRoot = $WorkspaceRoot
    EvidenceRoot = $EvidenceRoot
    ReleaseRoot = $ReleaseRoot
}
if ($CreateOneDriveFolders) {
    $initArgs.CreateOneDriveFolders = $true
}

& $initializer @initArgs | Write-Host

$repoState = foreach ($repo in $repositories) {
    $path = Join-Path $RepoRoot $repo.Name
    $gitPath = Join-Path $path '.git'
    if (-not (Test-Path -LiteralPath $gitPath)) {
        throw "Required repository is missing: $path"
    }

    Assert-CleanRepository -Path $path

    $branch = (git -C $path branch --show-current).Trim()
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($branch)) {
        throw "Repository is not on a named branch: $($repo.Name)"
    }

    $commit = (git -C $path rev-parse HEAD).Trim()
    if ($LASTEXITCODE -ne 0 -or $commit -notmatch '^[0-9a-f]{40}$') {
        throw "Unable to capture HEAD SHA: $($repo.Name)"
    }

    $origin = (git -C $path remote get-url origin).Trim()
    if ($LASTEXITCODE -ne 0) {
        throw "Unable to read origin URL: $($repo.Name)"
    }
    if ((Normalize-GitRemote $origin) -ne (Normalize-GitRemote $repo.Url)) {
        throw "Unexpected origin for $($repo.Name): $origin"
    }

    $upstream = (git -C $path rev-parse '@{u}').Trim()
    if ($LASTEXITCODE -ne 0 -or $upstream -notmatch '^[0-9a-f]{40}$') {
        throw "Unable to capture upstream SHA: $($repo.Name)"
    }
    if ($commit -ne $upstream) {
        throw "Repository is not at upstream HEAD: $($repo.Name)"
    }

    [pscustomobject]@{
        repository = $repo.Name
        branch = $branch
        commit = $commit
        upstream_commit = $upstream
        clean = $true
        origin_verified = $true
    }
}

if (@($repoState).Count -ne $repositories.Count) {
    throw 'A1 repository baseline is incomplete.'
}

$receipt = [ordered]@{
    schema = 'qps-cost-master.a1-repo-baseline.v1'
    phase = 'W002-bootstrap'
    action_id = 'A1'
    timestamp_utc = [DateTime]::UtcNow.ToString('o')
    repositories = @($repoState)
    required_repository_count = $repositories.Count
    verified_repository_count = @($repoState).Count
    clean_repository_count = @(
        $repoState | Where-Object clean
    ).Count
    origin_verified_count = @(
        $repoState | Where-Object origin_verified
    ).Count
    result = 'PASS'
    next_action = 'A2_BIND_GOVERNED_EVIDENCE_ROOT'
}

$logRoot = Join-Path $WorkspaceRoot '_logs'
if (-not (Test-Path -LiteralPath $logRoot)) {
    New-Item -ItemType Directory -Path $logRoot -Force | Out-Null
}
$receiptPath = Join-Path $logRoot 'A1_REPO_BASELINE_RECEIPT.json'
$receiptJson = $receipt | ConvertTo-Json -Depth 6
Set-Content -LiteralPath $receiptPath -Value $receiptJson -Encoding utf8

$receiptJson
Write-Host "A1 receipt: $receiptPath"
