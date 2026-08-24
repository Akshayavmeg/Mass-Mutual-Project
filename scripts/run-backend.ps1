<#
.SYNOPSIS
    Runs the backend development server (uvicorn, auto-reload) on port 8000.
#>

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$backendDir = Join-Path $repoRoot "apps\backend"

Push-Location $backendDir
try {
    & ".venv\Scripts\python.exe" -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
}
finally {
    Pop-Location
}
