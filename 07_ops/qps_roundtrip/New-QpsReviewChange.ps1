[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$LedgerPath,
    [Parameter(Mandatory = $true)][string]$SourceReleaseId,
    [Parameter(Mandatory = $true)][string]$ReviewFile,
    [Parameter(Mandatory = $true)][string]$ReviewLocation,
    [Parameter(Mandatory = $true)][string]$Reviewer,
    [Parameter(Mandatory = $true)][ValidateSet('DATA','CALCULATION_LOGIC','NARRATIVE','FORMATTING')][string]$ChangeClass,
    [Parameter(Mandatory = $true)][string]$Rationale,
    [string]$RequestedChange = '',
    [ValidateSet('OPEN','ACCEPTED','REJECTED','SUPERSEDED','IMPLEMENTED')][string]$Disposition = 'OPEN',
    [string]$TargetReleaseId = '',
    [string]$SourceCommit = '',
    [string]$Approver = ''
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$parent = Split-Path -Parent $LedgerPath
if ($parent -and -not (Test-Path -LiteralPath $parent)) {
    New-Item -ItemType Directory -Path $parent -Force | Out-Null
}

$existing = @()
if (Test-Path -LiteralPath $LedgerPath) {
    $existing = @(Import-Csv -LiteralPath $LedgerPath)
}

$next = $existing.Count + 1
$changeId = 'QPS-CHG-{0:D5}' -f $next
$timestamp = [DateTime]::UtcNow.ToString('o')

if ($Disposition -eq 'IMPLEMENTED' -and [string]::IsNullOrWhiteSpace($TargetReleaseId)) {
    throw 'TargetReleaseId is required when Disposition is IMPLEMENTED.'
}
if ($Disposition -eq 'IMPLEMENTED' -and [string]::IsNullOrWhiteSpace($SourceCommit)) {
    throw 'SourceCommit is required when Disposition is IMPLEMENTED.'
}

$record = [pscustomobject][ordered]@{
    change_id = $changeId
    source_release_id = $SourceReleaseId
    review_file = $ReviewFile
    review_location = $ReviewLocation
    reviewer = $Reviewer
    requested_utc = $timestamp
    change_class = $ChangeClass
    requested_change = $RequestedChange
    rationale = $Rationale
    disposition = $Disposition
    target_release_id = $TargetReleaseId
    source_commit = $SourceCommit
    approver = $Approver
}

@($existing + $record) | Export-Csv -LiteralPath $LedgerPath -NoTypeInformation -Encoding utf8

$record | ConvertTo-Json -Depth 3
