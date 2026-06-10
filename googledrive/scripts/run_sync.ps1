$ErrorActionPreference = "Stop"
Write-Host ">>> Initializing Agentic Bridge Integration Protocol" -ForegroundColor Cyan

if (-not $env:GEMINI_API_KEY) {
    Write-Warning "GEMINI_API_KEY unbound. Agent will use offline fallback routing for this session."
}

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$Engine = Join-Path $ScriptDir "drive_sync_agent.py"

& python -c "import google.genai" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "[*] Dependencies unverified. Staging google-genai package..." -ForegroundColor Yellow
    & python -m pip install google-genai -q
}

& python $Engine
