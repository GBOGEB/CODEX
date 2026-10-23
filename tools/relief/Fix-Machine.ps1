<#
.SYNOPSIS
  Scan this PC for what blocks Claude Code sessions (low C:, grown page file, too many sessions),
  run relief stages cheapest-first until it is unblocked, report, and offer the extended final
  step (restart) when only a reboot can give the space back.

  Stages, in order (each is skipped once C: >= -TargetGB and commit < -MaxCommitPct):
    temp      %TEMP% files older than 2 days (Claude task folders are never touched)
    pkgcache  pip and npm download caches (they refill on the next install)
    onedrive  unpinned OneDrive documents -> online-only; protected folders stay pinned
    sessions  memory commit too high -> copies /archive-idle to the clipboard and waits
  The claude process count is shown but not used: the desktop app runs ~20 helper processes
  of its own, so commit charge is the honest "too many sessions" signal.
  Extended final step:
    reboot    the page file only shrinks on restart (-Reboot schedules it; shutdown /a cancels)

.EXAMPLE
  .\Fix-Machine.ps1 -ListOnly             # scan + report, change nothing
.EXAMPLE
  .\Fix-Machine.ps1 -DryRun               # what each stage would free, change nothing
.EXAMPLE
  .\Fix-Machine.ps1                       # stages until unblocked, asks before each one
.EXAMPLE
  .\Fix-Machine.ps1 -Stage onedrive -Yes  # one stage, no prompt
.EXAMPLE
  .\Fix-Machine.ps1 -All -Reboot          # every stage, then offer a restart
.EXAMPLE
  .\Fix-Machine.ps1 -Watch 300            # re-scan every 5 min, beep when blocked
#>
param(
    [switch]$ListOnly,
    [switch]$DryRun,
    [string[]]$Stage,          # temp,pkgcache,onedrive,sessions: only these (in that order), ignoring the target
    [switch]$All,              # run every stage even when already unblocked
    [double]$TargetGB = 10,    # unblocked = C: free >= TargetGB ...
    [int]$MaxCommitPct = 80,   # ... and memory commit below this % (what grows the page file)
    [double]$MinFreeGB = 5,    # -Watch beeps below this
    [switch]$Yes,              # no prompts
    [switch]$Reboot,           # extended final step: schedule a restart (asks unless -Yes)
    [int]$Watch = 0,           # seconds between scans; 0 = scan once
    [switch]$Json,             # print the run record as JSON
    [switch]$InstallAlias,     # add a `relief` command to the PowerShell profile
    # OneDrive folders (relative to the OneDrive root) that may go online-only; 'Documents' is taken
    # child by child so its protected sub-folders are skipped.
    [string[]]$FreeDirs = @('Master_Output', 'Meetings', 'Microsoft Teams Chat Files', 'Pictures', 'LIBRARY',
                            'QPLANT_Contract_Review', 'QPS_LineS_Recovery', 'Documents'),
    # Canonical binaries and code: always stay pinned on this device.
    [string[]]$Protect = @('Master_Input', 'ariana_trace_project', 'Documents\.git', 'Documents\Development')
)

$ErrorActionPreference = 'Stop'
$Order = 'temp', 'pkgcache', 'onedrive', 'sessions'
# pwsh -File and the .cmd menu pass "temp,pkgcache" as one string: split it here.
$Stage = @($Stage -split '[,\s]+' | Where-Object { $_ })
$bad = $Stage | Where-Object { $Order -notcontains $_ }
if ($bad) { throw "Unknown stage: $($bad -join ', '). Use: $($Order -join ', ')" }
$od = if ($env:OneDriveCommercial) { $env:OneDriveCommercial } else { $env:OneDrive }

$PINNED = 0x80000; $UNPINNED = 0x100000; $CLOUD = 0x400000 -bor 0x1000   # recall-on-access | offline

if ($InstallAlias) {
    $line = "function relief { & '$PSCommandPath' @args }"
    $prof = $PROFILE.CurrentUserAllHosts
    if (-not (Test-Path $prof) -or -not (Select-String -Path $prof -SimpleMatch $line -Quiet)) {
        New-Item -ItemType File -Force $prof | Out-Null
        Add-Content $prof $line
    }
    "Added to $prof : relief  (open a new PowerShell window, then e.g.  relief -ListOnly)"
    return
}

function Files([string]$Dir) {
    $o = [IO.EnumerationOptions]::new(); $o.RecurseSubdirectories = $true; $o.IgnoreInaccessible = $true; $o.AttributesToSkip = 0
    if (Test-Path -LiteralPath $Dir) { [IO.DirectoryInfo]::new($Dir).EnumerateFiles('*', $o) }
}
function GB([double]$Bytes) { [math]::Round($Bytes / 1GB, 2) }

function Scan {
    $os = Get-CimInstance Win32_OperatingSystem
    $pf = Get-CimInstance Win32_PageFileUsage | Select-Object -First 1
    $claude = @(Get-Process claude -EA 0)
    $s = [ordered]@{
        Time        = (Get-Date).ToString('yyyy-MM-dd HH:mm')
        FreeGB      = GB (Get-PSDrive C).Free
        PageAllocGB = [math]::Round($pf.AllocatedBaseSize / 1KB, 1)
        PageUsedGB  = [math]::Round($pf.CurrentUsage / 1KB, 1)
        CommitGB    = [math]::Round(($os.TotalVirtualMemorySize - $os.FreeVirtualMemory) / 1MB, 1)
        CommitMaxGB = [math]::Round($os.TotalVirtualMemorySize / 1MB, 1)
        Claude      = $claude.Count
        ClaudeRamGB = GB ($claude | Measure-Object WorkingSet64 -Sum).Sum
    }
    $s.RebootGB  = [math]::Max(0, [math]::Round($s.PageAllocGB - [math]::Max($s.PageUsedGB * 2, 8), 1))
    $s.CommitPct = [int](100 * $s.CommitGB / $s.CommitMaxGB)
    $s.Unblocked = $s.FreeGB -ge $TargetGB -and $s.CommitPct -lt $MaxCommitPct
    $s.Blocked   = $s.FreeGB -lt $MinFreeGB -or $s.CommitPct -ge 90
    [pscustomobject]$s
}
function Show($s) {
    $c = if ($s.Blocked) { 'Red' } elseif ($s.Unblocked) { 'Green' } else { 'Yellow' }
    Write-Host ("{0}  C: free {1:N2} GB | pagefile {2:N1} GB ({3:N1} in use) | commit {4:N1}/{5:N1} GB ({6}%) | claude procs {7} ({8:N1} GB RAM)" -f `
        $s.Time, $s.FreeGB, $s.PageAllocGB, $s.PageUsedGB, $s.CommitGB, $s.CommitMaxGB, $s.CommitPct, $s.Claude, $s.ClaudeRamGB) -ForegroundColor $c
}

# ---- stages: Measure returns the GB it expects to free; Run does it --------------------------
$tempCut = (Get-Date).AddDays(-2)
function TempFiles { Files $env:TEMP | Where-Object { $_.LastWriteTime -lt $tempCut -and $_.FullName -notmatch '\\claude\\' } }
function PipDir { if (Get-Command python -EA 0) { (& python -m pip cache dir 2>$null) } }
function NpmDir { if (Get-Command npm -EA 0) { (& npm config get cache 2>$null) } }
function OneDriveTargets {
    if (-not $od) { return }   # no OneDrive on this machine: the stage frees nothing
    foreach ($f in $FreeDirs) {
        $p = Join-Path $od $f
        if (-not (Test-Path -LiteralPath $p)) { continue }
        if ($f -ne 'Documents') { $p; continue }
        # Documents holds protected sub-folders: take its children one by one.
        foreach ($c in Get-ChildItem -LiteralPath $p -Force) {
            if ($Protect -notcontains "Documents\$($c.Name)") { $c.FullName }
        }
    }
}
function LocalUnpinned([string]$Path) {
    $items = if (Test-Path -LiteralPath $Path -PathType Leaf) { , (Get-Item -LiteralPath $Path -Force) } else { Files $Path }
    foreach ($f in $items) { $a = [int]$f.Attributes; if (-not ($a -band ($CLOUD -bor $PINNED))) { $f.Length } }
}

$Stages = @{
    temp = @{
        Why     = "%TEMP% files older than 2 days"
        Measure = { GB (TempFiles | Measure-Object Length -Sum).Sum }
        Run     = {
            TempFiles | ForEach-Object { Remove-Item -LiteralPath $_.FullName -Force -EA SilentlyContinue }
            Get-ChildItem $env:TEMP -Directory -Force -EA 0 | Where-Object { $_.Name -ne 'claude' -and $_.LastWriteTime -lt $tempCut } |
                Where-Object { -not (Get-ChildItem -LiteralPath $_.FullName -Recurse -Force -File -EA 0 | Select-Object -First 1) } |
                ForEach-Object { Remove-Item -LiteralPath $_.FullName -Recurse -Force -EA SilentlyContinue }
        }
    }
    pkgcache = @{
        Why     = "pip and npm download caches"
        Measure = { GB (@(PipDir; NpmDir) | Where-Object { $_ -and (Test-Path $_) } | ForEach-Object { Files $_ } | Measure-Object Length -Sum).Sum }
        Run     = {
            if (PipDir) { & python -m pip cache purge 2>&1 | Out-Null }
            if (NpmDir) { & npm cache clean --force 2>&1 | Out-Null }
        }
    }
    onedrive = @{
        Why     = "unpinned OneDrive documents -> online-only (protected: $($Protect -join ', '))"
        Measure = { GB (OneDriveTargets | ForEach-Object { LocalUnpinned $_ } | Measure-Object -Sum).Sum }
        Run     = {
            foreach ($t in OneDriveTargets) {
                if (Test-Path -LiteralPath $t -PathType Container) { & attrib.exe -P +U "$t\*" /S /D 2>&1 | Out-Null }
                else { & attrib.exe -P +U "$t" 2>&1 | Out-Null }
            }
            # guard: the protected folders must still be pinned
            foreach ($p in $Protect) {
                $n = 0; $bad = 0
                foreach ($f in Files (Join-Path $od $p)) { $n++; if (-not ([int]$f.Attributes -band $PINNED)) { $bad++ }; if ($n -ge 2000) { break } }
                if ($bad) { Write-Warning "$p : $bad of $n sampled files are not pinned. Re-pin: attrib +P -U `"$(Join-Path $od $p)\*`" /S /D" }
            }
            Write-Host "  OneDrive releases the space in the background; re-scan in a few minutes." -ForegroundColor DarkGray
        }
    }
    sessions = @{
        Why     = "memory commit at or above $MaxCommitPct% keeps growing the page file"
        Measure = { 0 }
        Run     = {
            $s = Scan
            if ($s.CommitPct -lt $MaxCommitPct) { Write-Host "  commit $($s.CommitPct)%: fine."; return }
            Set-Clipboard '/archive-idle'
            Write-Host "  commit $($s.CommitPct)%. In any Claude Code session paste /archive-idle (copied to the clipboard)." -ForegroundColor Yellow
            Write-Host "  It lists idle sessions and archives them; running sessions are kept."
            if (-not $Yes) { Read-Host '  Press Enter when done' | Out-Null }
        }
    }
}

function Confirm([string]$Q) { if ($Yes) { return $true }; (Read-Host "$Q [y/N]") -match '^(y|yes)$' }

# ---- 1. scan ---------------------------------------------------------------------------------
if ($Watch -gt 0) {
    while ($true) {
        $s = Scan; Show $s
        if ($s.Blocked) { [console]::Beep(880, 300); Write-Host '  BLOCKED: run  .\Fix-Machine.ps1  (or  relief)' -ForegroundColor Red }
        Start-Sleep $Watch
    }
}
$start = Scan; Show $start
if ($ListOnly) {
    if ($start.RebootGB -gt 2) { Write-Host "  A restart would give back about $($start.RebootGB) GB of page file." -ForegroundColor DarkGray }
    if ($Json) { $start | ConvertTo-Json }
    return
}

# ---- 2. stages, cheapest first, until unblocked ---------------------------------------------
$run = if ($Stage) { $Order | Where-Object { $Stage -contains $_ } } else { $Order }
$results = [Collections.Generic.List[object]]::new()
foreach ($name in $run) {
    $before = Scan
    if (-not $Stage -and -not $All -and -not $DryRun -and $before.Unblocked) {
        Write-Host "Unblocked (C: >= $TargetGB GB, commit < $MaxCommitPct%): stopping before '$name'." -ForegroundColor Green
        break
    }
    $st = $Stages[$name]
    $est = & $st.Measure
    Write-Host ("`n[{0}] {1}: about {2:N2} GB" -f $name, $st.Why, $est) -ForegroundColor Cyan
    $status = 'DRYRUN'
    if (-not $DryRun) {
        if (Confirm "  Run stage '$name'?") { & $st.Run; $status = 'DONE' } else { $status = 'SKIPPED' }
    }
    $after = Scan
    $results.Add([pscustomobject]@{ Stage = $name; EstimateGB = $est; FreeBeforeGB = $before.FreeGB; FreeAfterGB = $after.FreeGB; Status = $status })
}

# ---- 3. extended final step: restart for the page file --------------------------------------
$end = Scan
$rebootStatus = 'not needed'
if ($end.RebootGB -gt 2) {
    $rebootStatus = 'advised'
    Write-Host "`n[reboot] page file is $($end.PageAllocGB) GB but only $($end.PageUsedGB) GB is in use; a restart gives back about $($end.RebootGB) GB." -ForegroundColor Cyan
    if ($Reboot -and -not $DryRun) {
        if (Confirm '  Restart in 5 minutes? (ends every session; cancel with  shutdown /a)') {
            & shutdown.exe /r /t 300 /c 'Fix-Machine: restart to shrink the page file. Cancel: shutdown /a'
            $rebootStatus = 'scheduled'
        }
    }
    elseif (-not $Reboot) { Write-Host '  Run again with -Reboot to schedule it, or restart when your sessions are done.' }
}

# ---- 4. report + log -------------------------------------------------------------------------
Write-Host "`nRESULT" -ForegroundColor Cyan
$results | Format-Table -AutoSize | Out-String | Write-Host
Show $end
$state = if ($end.Unblocked) { 'UNBLOCKED' } elseif ($end.Blocked) { 'BLOCKED' } else { 'TIGHT' }
Write-Host "$state   (reboot: $rebootStatus)" -ForegroundColor $(if ($end.Unblocked) { 'Green' } elseif ($end.Blocked) { 'Red' } else { 'Yellow' })

$record = [ordered]@{ Start = $start; Stages = $results; End = $end; State = $state; Reboot = $rebootStatus; DryRun = [bool]$DryRun }
$logDir = Join-Path $env:LOCALAPPDATA 'machine-relief\logs'
New-Item -ItemType Directory -Force $logDir | Out-Null
$log = Join-Path $logDir ((Get-Date -Format 'yyyyMMdd-HHmmss') + '.json')
$record | ConvertTo-Json -Depth 5 | Set-Content -Encoding utf8 $log
Write-Host "log: $log" -ForegroundColor DarkGray
if ($Json) { $record | ConvertTo-Json -Depth 5 }
if ($state -eq 'BLOCKED') { exit 2 }
