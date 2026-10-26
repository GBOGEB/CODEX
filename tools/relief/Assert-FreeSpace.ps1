#requires -Version 5.1
<#
.SYNOPSIS
  Read-only, fail-closed preflight for starting local coding sessions: disk space, memory
  commit charge and git fsmonitor daemons.
.DESCRIPTION
  BLOCKED (exit 2) when the drive has less than -MinFreeGB free, or commit charge is at or
  above -MaxCommitPct (90 %). WARN (exit 0) when commit charge is at or above -WarnCommitPct
  (80 %) or more than -MaxFsmonitor (20) `git fsmonitor--daemon run` processes are alive.
  PASS (exit 0) otherwise. UNREADABLE (exit 3) when disk or commit state cannot be read.

  Measurements avoid CIM, which costs 0.6-1.2 s per call under load: free space comes from
  System.IO.DriveInfo, commit charge from GlobalMemoryStatusEx and the fsmonitor command lines
  from NtQueryInformationProcess, both through a P/Invoke type built with Reflection.Emit (no
  Add-Type compile). The script body takes well under 200 ms; pwsh startup adds 1.7-2.6 s
  under load, so allow for that in any hook timeout.

  -Hook prints exactly one line for a Claude Code SessionStart hook: PASS and WARN go to
  stdout with exit 0 (Claude sees the line as context), BLOCKED goes to stderr with exit 2
  (shown to the user; SessionStart hooks cannot block a session), UNREADABLE goes to stderr
  with exit 3.

  Never deletes files, stops processes, restarts the machine, or starts a session.
  Fix-Machine.ps1 reads the -Json receipt for its fsmonitor stage.
.EXAMPLE
  pwsh -NoProfile -File tools/relief/Assert-FreeSpace.ps1 -Drive C: -MinFreeGB 5
.EXAMPLE
  pwsh -NoProfile -NonInteractive -File tools/relief/Assert-FreeSpace.ps1 -Hook
.EXAMPLE
  pwsh -NoProfile -File tools/relief/Assert-FreeSpace.ps1 -Json
#>
[CmdletBinding()]
param(
    [ValidatePattern('^[A-Za-z]:$')][string] $Drive = 'C:',
    [ValidateRange(0.1, 100000)][double] $MinFreeGB = 5,
    [ValidateRange(1, 100)][double] $MaxCommitPct = 90,
    [ValidateRange(1, 100)][double] $WarnCommitPct = 80,
    [ValidateRange(0, 100000)][int] $MaxFsmonitor = 20,
    [switch] $Hook,
    [switch] $Json,
    # Test seams: replace a measurement so the threshold logic runs on any OS.
    [Nullable[double]] $SimulateFreeGB,
    [Nullable[double]] $SimulateCommitPct,
    [Nullable[int]] $SimulateFsmonitorCount,
    [Nullable[double]] $SimulateFsmonitorGB,
    [switch] $SimulateUnreadable
)
$ErrorActionPreference = 'Stop'
$clock = [Diagnostics.Stopwatch]::StartNew()
$Marshal = [Runtime.InteropServices.Marshal]

function Get-NativeApi {
    $t = 'CodexRelief.Native' -as [type]
    if ($t) { return $t }
    $ab = [Reflection.Emit.AssemblyBuilder]::DefineDynamicAssembly(
        [Reflection.AssemblyName]::new('CodexRelief.Native'), [Reflection.Emit.AssemblyBuilderAccess]::Run)
    $tb = $ab.DefineDynamicModule('CodexRelief.Native').DefineType('CodexRelief.Native', 'Public, Abstract, Sealed, Class')
    foreach ($d in @(
            @('GlobalMemoryStatusEx', 'kernel32.dll', [bool], @([IntPtr])),
            @('OpenProcess', 'kernel32.dll', [IntPtr], @([int], [bool], [int])),
            @('NtQueryInformationProcess', 'ntdll.dll', [int], @([IntPtr], [int], [IntPtr], [int], [int].MakeByRefType())),
            @('CloseHandle', 'kernel32.dll', [bool], @([IntPtr])))) {
        $m = $tb.DefinePInvokeMethod($d[0], $d[1], 'Public, Static, PinvokeImpl, HideBySig', 'Standard',
            $d[2], [type[]]$d[3], 'Winapi', 'Unicode')
        $m.SetImplementationFlags('PreserveSig')
    }
    $tb.CreateType()
}

function Get-FreeGB([string] $Name) {
    $di = [IO.DriveInfo]::new($Name)
    if (-not $di.IsReady) { throw "Drive $Name is not ready" }
    [double]$di.TotalFreeSpace / 1GB
}

function Get-Commit {
    # MEMORYSTATUSEX: ullTotalPageFile (offset 24) is the commit limit, ullAvailPageFile (32) what is left.
    $api = Get-NativeApi
    $buf = $Marshal::AllocHGlobal(64)
    try {
        $Marshal::WriteInt32($buf, 0, 64)
        if (-not $api::GlobalMemoryStatusEx($buf)) { throw 'GlobalMemoryStatusEx failed' }
        $limit = [double]$Marshal::ReadInt64($buf, 24)
        $avail = [double]$Marshal::ReadInt64($buf, 32)
    } finally { $Marshal::FreeHGlobal($buf) }
    if ($limit -le 0) { throw 'commit limit reported as 0' }
    @{ Pct = 100 * ($limit - $avail) / $limit; UsedGB = ($limit - $avail) / 1GB; LimitGB = $limit / 1GB }
}

function Get-FsmonitorDaemons {
    # One `git fsmonitor--daemon run` per worktree that has core.fsmonitor=true. The command line is
    # read with ProcessCommandLineInformation (class 60) so other git.exe processes are never counted.
    $api = Get-NativeApi
    $cap = 16384
    $buf = $Marshal::AllocHGlobal($cap)
    try {
        foreach ($p in [Diagnostics.Process]::GetProcessesByName('git')) {
            $h = $api::OpenProcess(0x1000, $false, $p.Id)   # PROCESS_QUERY_LIMITED_INFORMATION
            if ($h -eq [IntPtr]::Zero) { continue }
            $ret = 0
            try { $status = $api::NtQueryInformationProcess($h, 60, $buf, $cap, [ref]$ret) }
            finally { $null = $api::CloseHandle($h) }
            if ($status -ne 0) { continue }
            $len = [int][uint16]$Marshal::ReadInt16($buf, 0)
            $cl = $Marshal::PtrToStringUni($Marshal::ReadIntPtr($buf, [IntPtr]::Size), [int]($len / 2))
            if ($cl -match '\sfsmonitor--daemon\s+run(\s|$)') {
                [pscustomobject]@{ Id = $p.Id; PrivateBytes = [double]$p.PrivateMemorySize64 }
            }
        }
    } finally { $Marshal::FreeHGlobal($buf) }
}

try {
    if ($WarnCommitPct -gt $MaxCommitPct) { throw "-WarnCommitPct ($WarnCommitPct) is above -MaxCommitPct ($MaxCommitPct)" }
    if ($SimulateUnreadable) { throw 'simulated unreadable state' }
    $simulated = $null -ne $SimulateFreeGB -or $null -ne $SimulateCommitPct -or $null -ne $SimulateFsmonitorCount

    $freeGB = if ($null -ne $SimulateFreeGB) { [double]$SimulateFreeGB } else { Get-FreeGB $Drive }
    $commit = if ($null -ne $SimulateCommitPct) { @{ Pct = [double]$SimulateCommitPct; UsedGB = $null; LimitGB = $null } } else { Get-Commit }

    # fsmonitor is advisory: a failed read is reported as unknown, never as UNREADABLE.
    $fsCount = $null; $fsGB = $null; $fsPids = @()
    if ($null -ne $SimulateFsmonitorCount) {
        $fsCount = [int]$SimulateFsmonitorCount
        $fsGB = if ($null -ne $SimulateFsmonitorGB) { [double]$SimulateFsmonitorGB } else { 0.0 }
    } else {
        # Plain loops, no Measure-Object/Select-Object: loading their module costs 100+ ms cold.
        try {
            $daemons = @(Get-FsmonitorDaemons)
            $bytes = 0.0
            foreach ($d in $daemons) { $bytes += $d.PrivateBytes; $fsPids += $d.Id }
            $fsCount = $daemons.Count
            $fsGB = $bytes / 1GB
        } catch { $fsCount = $null }
    }

    $reasons = [Collections.Generic.List[string]]::new()
    $next = [Collections.Generic.List[string]]::new()
    if ($freeGB -lt $MinFreeGB) { $reasons.Add('low_space'); $next.Add('run tools/relief/Fix-Machine.ps1 -DryRun') }
    if ($commit.Pct -ge $MaxCommitPct) { $reasons.Add('commit_high') }
    elseif ($commit.Pct -ge $WarnCommitPct) { $reasons.Add('commit_warn') }
    if ($commit.Pct -ge $WarnCommitPct) { $next.Add('archive idle sessions (/archive-idle)') }
    if ($null -ne $fsCount -and $fsCount -gt $MaxFsmonitor) {
        $reasons.Add('fsmonitor_many'); $next.Add('Fix-Machine.ps1 -Stage fsmonitor -Yes')
    }
    $verdict = if ($reasons -contains 'low_space' -or $reasons -contains 'commit_high') { 'BLOCKED' }
               elseif ($reasons.Count) { 'WARN' } else { 'PASS' }

    $inv = [Globalization.CultureInfo]::InvariantCulture   # one parseable line on every locale
    $fsText = if ($null -eq $fsCount) { 'fsmonitor n/a' } else {
        [string]::Format($inv, 'fsmonitor {0} ({1:F2} GiB, warn >{2})', $fsCount, $fsGB, $MaxFsmonitor) }
    $line = [string]::Format($inv, 'RELIEF_GUARD {0}: {1} {2:F1} GiB free (min {3}) | commit {4:F1}% (warn {5}, block {6}) | {7}',
        $verdict, $Drive, $freeGB, $MinFreeGB, $commit.Pct, $WarnCommitPct, $MaxCommitPct, $fsText)
    if ($next.Count) { $line += ' | next: ' + ($next -join '; ') }
    $line += ' | ' + $clock.ElapsedMilliseconds + ' ms'
    $exitCode = if ($verdict -eq 'BLOCKED') { 2 } else { 0 }

    if ($Hook) {
        if ($exitCode -eq 0) { [Console]::Out.WriteLine($line) } else { [Console]::Error.WriteLine($line) }
        exit $exitCode
    }
    if ($Json) {
        [ordered]@{
            schema          = 'codex.relief.disk_preflight.v2'
            verdict         = $verdict
            reasons         = @($reasons)
            drive           = $Drive
            free_gb         = [math]::Round($freeGB, 3)
            minimum_gb      = $MinFreeGB
            commit_pct      = [math]::Round($commit.Pct, 1)
            commit_warn_pct = $WarnCommitPct
            commit_max_pct  = $MaxCommitPct
            commit_used_gb  = $(if ($null -ne $commit.UsedGB) { [math]::Round($commit.UsedGB, 2) })
            commit_limit_gb = $(if ($null -ne $commit.LimitGB) { [math]::Round($commit.LimitGB, 2) })
            fsmonitor       = [ordered]@{
                count      = $fsCount
                private_gb = $(if ($null -ne $fsGB) { [math]::Round($fsGB, 3) })
                warn_above = $MaxFsmonitor
                pids       = @($fsPids)
            }
            simulated       = $simulated
            elapsed_ms      = $clock.ElapsedMilliseconds
            read_only       = $true
        } | ConvertTo-Json -Compress -Depth 4
        exit $exitCode
    }
    Write-Host $line
    if ($exitCode -ne 0) {
        Write-Warning 'Do not start a new session; inspect with tools/relief/Fix-Machine.ps1 -ListOnly first.'
    }
    exit $exitCode
} catch {
    $msg = 'RELIEF_GUARD UNREADABLE: ' + $_.Exception.Message
    if ($Hook) { [Console]::Error.WriteLine($msg) } else { Write-Error $msg -ErrorAction Continue }
    exit 3
}
