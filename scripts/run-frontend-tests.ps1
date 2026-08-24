<#
.SYNOPSIS
    Runs the frontend automated test suite.
#>

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$frontendDir = Join-Path $repoRoot "apps\frontend"

Push-Location $frontendDir
try {
    npm run test
}
finally {
    Pop-Location
}
