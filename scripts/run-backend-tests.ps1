<#
.SYNOPSIS
    Runs the backend automated test suite.
#>

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$backendDir = Join-Path $repoRoot "apps\backend"

Push-Location $backendDir
try {
    & ".venv\Scripts\python.exe" -m pytest -v
}
finally {
    Pop-Location
}
