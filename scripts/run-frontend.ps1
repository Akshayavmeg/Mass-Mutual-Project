<#
.SYNOPSIS
    Runs the frontend development server (Vite) on port 3000.
#>

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$frontendDir = Join-Path $repoRoot "apps\frontend"

Push-Location $frontendDir
try {
    npm run dev
}
finally {
    Pop-Location
}
