<# Compatibility shim for googledrive/scripts/run_sync.ps1. #>

param(
    [string]$ExchangeDir = "googledrive",
    [switch]$Json,
    [switch]$InstallDependencies
)

if ($ExchangeDir -ne "googledrive") {
    Write-Warning "ExchangeDir is ignored by this compatibility shim; canonical runner uses googledrive/."
}
if ($Json) {
    Write-Warning "Json is ignored by this compatibility shim; canonical runner writes JSONL audit records."
}
if ($InstallDependencies) {
    Write-Warning "InstallDependencies is ignored by this compatibility shim; use googledrive/scripts/run_sync.ps1 directly for dependency setup."
}

$Target = Join-Path $PSScriptRoot "../googledrive/scripts/run_sync.ps1"
& $Target
