$ErrorActionPreference = "Stop"
Write-Host ">>> Executing Offline Baseline Configuration Checks" -ForegroundColor Yellow
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$Engine = Join-Path $ScriptDir "reconcile_drive.py"
& python $Engine
