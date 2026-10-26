#requires -Version 5.1
<#
.SYNOPSIS
  Plain PowerShell test for tools/relief/Assert-FreeSpace.ps1: threshold logic, exit codes and the
  one-line -Hook output. Measurements are replaced with the -Simulate* seams, so it runs on any OS.
  On Windows it also runs one real (unsimulated) -Hook call and checks its shape.
.OUTPUTS
  One JSON line {result, passed, failed, failures}; exit 1 when any case fails.
#>
[CmdletBinding()]
param([string] $Guard = (Join-Path (Split-Path -Parent $PSScriptRoot) 'Assert-FreeSpace.ps1'))
$ErrorActionPreference = 'Stop'
$exe = (Get-Process -Id $PID).Path
$errFile = [IO.Path]::GetTempFileName()
$failures = [Collections.Generic.List[string]]::new()
$passed = 0

function Invoke-Guard([string[]] $GuardArgs) {
    $out = @(& $exe -NoProfile -NonInteractive -File $Guard @GuardArgs 2> $errFile)
    $code = $LASTEXITCODE
    $err = @(Get-Content -LiteralPath $errFile | Where-Object { $_ -ne '' })
    [pscustomobject]@{ Code = $code; Out = @($out | Where-Object { $_ -ne '' }); Err = $err }
}

function Check([string] $Name, [bool] $Ok, [string] $Detail) {
    if ($Ok) { $script:passed++ } else { $script:failures.Add("$Name : $Detail") }
}

# -Hook cases: name, args, expected exit, expected verdict, stream ('out'|'err'), required substring
$base = @('-Hook', '-SimulateFsmonitorCount', '3', '-SimulateFsmonitorGB', '0.1')
$cases = @(
    @('pass',              @('-SimulateFreeGB', '50', '-SimulateCommitPct', '50'),                   0, 'PASS',       'out', 'commit 50.0%'),
    @('commit warn edge',  @('-SimulateFreeGB', '50', '-SimulateCommitPct', '80'),                   0, 'WARN',       'out', '/archive-idle'),
    @('commit below warn', @('-SimulateFreeGB', '50', '-SimulateCommitPct', '79.9'),                 0, 'PASS',       'out', 'warn 80, block 90'),
    @('commit just below', @('-SimulateFreeGB', '50', '-SimulateCommitPct', '89.9'),                 0, 'WARN',       'out', 'commit 89.9%'),
    @('commit block edge', @('-SimulateFreeGB', '50', '-SimulateCommitPct', '90'),                   2, 'BLOCKED',    'err', 'commit 90.0%'),
    @('low space',         @('-SimulateFreeGB', '4.9', '-SimulateCommitPct', '50'),                  2, 'BLOCKED',    'err', 'Fix-Machine.ps1 -DryRun'),
    @('space at minimum',  @('-SimulateFreeGB', '5', '-SimulateCommitPct', '50'),                    0, 'PASS',       'out', 'C: 5.0 GiB free'),
    @('custom thresholds', @('-SimulateFreeGB', '50', '-SimulateCommitPct', '65', '-WarnCommitPct', '60', '-MaxCommitPct', '70'), 0, 'WARN', 'out', 'warn 60, block 70'),
    @('custom block',      @('-SimulateFreeGB', '50', '-SimulateCommitPct', '70', '-WarnCommitPct', '60', '-MaxCommitPct', '70'), 2, 'BLOCKED', 'err', 'block 70'),
    @('bad thresholds',    @('-SimulateFreeGB', '50', '-SimulateCommitPct', '50', '-WarnCommitPct', '95'),  3, 'UNREADABLE', 'err', 'WarnCommitPct'),
    @('unreadable',        @('-SimulateUnreadable'),                                                 3, 'UNREADABLE', 'err', 'simulated')
)
foreach ($c in $cases) {
    $r = Invoke-Guard ($base + $c[1])
    $lines = @(if ($c[4] -eq 'out') { $r.Out } else { $r.Err })
    $other = @(if ($c[4] -eq 'out') { $r.Err } else { $r.Out })
    Check $c[0] ($r.Code -eq $c[2]) "exit $($r.Code), expected $($c[2])"
    Check "$($c[0]) one line" ($lines.Count -eq 1 -and $other.Count -eq 0) "out=[$($r.Out -join ' / ')] err=[$($r.Err -join ' / ')]"
    if ($lines.Count -ge 1) {
        Check "$($c[0]) verdict" ($lines[0].StartsWith("RELIEF_GUARD $($c[3]):")) $lines[0]
        Check "$($c[0]) text" ($lines[0].Contains($c[5])) "missing '$($c[5])' in: $($lines[0])"
    }
}

# fsmonitor: warn only when MORE than -MaxFsmonitor daemons run
foreach ($f in @(@('20', 'PASS'), @('21', 'WARN'))) {
    $r = Invoke-Guard @('-Hook', '-SimulateFreeGB', '50', '-SimulateCommitPct', '50', '-SimulateFsmonitorCount', $f[0], '-SimulateFsmonitorGB', '2.3')
    $line = if ($r.Out.Count) { $r.Out[0] } else { '' }
    Check "fsmonitor $($f[0])" ($r.Code -eq 0 -and $line.StartsWith("RELIEF_GUARD $($f[1]):")) "exit $($r.Code): $line"
}
$r = Invoke-Guard @('-Hook', '-SimulateFreeGB', '50', '-SimulateCommitPct', '50', '-SimulateFsmonitorCount', '51', '-SimulateFsmonitorGB', '2.3')
Check 'fsmonitor text' ($r.Out.Count -eq 1 -and $r.Out[0].Contains('fsmonitor 51 (2.30 GiB, warn >20)') -and $r.Out[0].Contains('-Stage fsmonitor')) "$($r.Out)"

# -Json receipt
$r = Invoke-Guard @('-Json', '-SimulateFreeGB', '3', '-SimulateCommitPct', '91', '-SimulateFsmonitorCount', '30', '-SimulateFsmonitorGB', '1.5')
try {
    $j = ($r.Out -join '') | ConvertFrom-Json
    Check 'json exit' ($r.Code -eq 2) "exit $($r.Code)"
    Check 'json schema' ($j.schema -eq 'codex.relief.disk_preflight.v2') $j.schema
    Check 'json verdict' ($j.verdict -eq 'BLOCKED') $j.verdict
    Check 'json reasons' ((@($j.reasons) -join ',') -eq 'low_space,commit_high,fsmonitor_many') (@($j.reasons) -join ',')
    Check 'json fsmonitor' ($j.fsmonitor.count -eq 30 -and $j.fsmonitor.private_gb -eq 1.5) ($j.fsmonitor | ConvertTo-Json -Compress)
    Check 'json simulated' ($j.simulated -eq $true -and $j.read_only -eq $true) "simulated=$($j.simulated)"
} catch { Check 'json parse' $false "$($_.Exception.Message): $($r.Out)" }

# Real measurement, Windows only: shape and exit code, not the values.
if ([Environment]::OSVersion.Platform -eq 'Win32NT') {
    $r = Invoke-Guard @('-Hook')
    $lines = @($r.Out) + @($r.Err)
    Check 'real hook exit' (@(0, 2) -contains $r.Code) "exit $($r.Code): $($lines -join ' / ')"
    Check 'real hook one line' ($lines.Count -eq 1 -and $lines[0] -match '^RELIEF_GUARD (PASS|WARN|BLOCKED): .*commit [\d.]+% .*fsmonitor \d+ .*\| \d+ ms$') ($lines -join ' / ')
    $r = Invoke-Guard @('-Json')
    try {
        $j = ($r.Out -join '') | ConvertFrom-Json
        Check 'real json commit' ($j.commit_pct -gt 0 -and $j.commit_pct -le 100 -and $j.commit_limit_gb -gt 0) "commit_pct=$($j.commit_pct)"
        Check 'real json fsmonitor' ($null -ne $j.fsmonitor.count -and @($j.fsmonitor.pids).Count -eq $j.fsmonitor.count) "count=$($j.fsmonitor.count)"
    } catch { Check 'real json parse' $false "$($_.Exception.Message): $($r.Out)" }
}

Remove-Item -LiteralPath $errFile -Force -ErrorAction SilentlyContinue
[ordered]@{
    result   = $(if ($failures.Count) { 'FAIL' } else { 'PASS' })
    passed   = $passed
    failed   = $failures.Count
    failures = @($failures)
} | ConvertTo-Json -Compress
if ($failures.Count) { exit 1 }
