<#
.SYNOPSIS
    Installs frontend dependencies.
#>

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$frontendDir = Join-Path $repoRoot "apps\frontend"

Push-Location $frontendDir
try {
    Write-Host "Installing frontend dependencies..."
    npm install

    if (-not (Test-Path ".env") -and (Test-Path ".env.example")) {
        Copy-Item ".env.example" ".env"
        Write-Host "Created apps/frontend/.env from .env.example -- edit it with your local values."
    }

    Write-Host "Frontend setup complete."
}
finally {
    Pop-Location
}
