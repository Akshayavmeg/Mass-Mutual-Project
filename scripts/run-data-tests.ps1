<#
.SYNOPSIS
    Regenerates the synthetic data foundation and runs its validation tests.
#>

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$backendPython = Join-Path $repoRoot "apps\backend\.venv\Scripts\python.exe"

Push-Location $repoRoot
try {
    Write-Host "Generating synthetic data..."
    & $backendPython "scripts\generate_synthetic_data.py"

    Write-Host "Running data validation tests..."
    & $backendPython -m pytest "tests\unit" -v
}
finally {
    Pop-Location
}
