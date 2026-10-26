#requires -Version 5.1
<#
.SYNOPSIS
  Read-only, fail-closed disk preflight for starting local coding sessions.
.DESCRIPTION
  Exit 0 only when the requested local drive reports >= MinFreeGB.
  Exit 2 below threshold; exit 3 if disk state cannot be read.
  Never deletes files, restarts the machine, or starts a session.
.EXAMPLE
  pwsh -NoProfile -File tools/relief/Assert-FreeSpace.ps1 -Drive C: -MinFreeGB 5
#>
[CmdletBinding()]
param(
    [ValidatePattern('^[A-Za-z]:$')][string] $Drive = 'C:',
    [ValidateRange(0.1, 100000)][double] $MinFreeGB = 5,
    [switch] $Json
)
$ErrorActionPreference = 'Stop'
try {
    $disk = Get-CimInstance -ClassName Win32_LogicalDisk -Filter "DeviceID='$Drive'" -ErrorAction Stop
    if ($null -eq $disk -or $null -eq $disk.FreeSpace) {
        throw "Drive $Drive missing or free space unavailable"
    }
    $freeGB = [math]::Round(([double]$disk.FreeSpace / 1GB), 3)
    $passed = [double]$disk.FreeSpace -ge ($MinFreeGB * 1GB)
    $receipt = [ordered]@{
        schema = 'codex.relief.disk_preflight.v1'
        drive = $Drive
        free_gb = $freeGB
        minimum_gb = $MinFreeGB
        verdict = $(if ($passed) { 'PASS' } else { 'BLOCKED_LOW_SPACE' })
        read_only = $true
    }
    if ($Json) {
        $receipt | ConvertTo-Json -Compress
    } else {
        Write-Host ("DISK_PREFLIGHT {0}: {1} GiB free on {2}; minimum {3} GiB" -f $receipt.verdict,$freeGB,$Drive,$MinFreeGB)
    }
    if (-not $passed) {
        Write-Warning "Do not start a new session; inspect with tools/relief/Fix-Machine.ps1 -ListOnly first."
        exit 2
    }
    exit 0
} catch {
    Write-Error ("DISK_PREFLIGHT UNREADABLE: " + $_.Exception.Message) -ErrorAction Continue
    exit 3
}
