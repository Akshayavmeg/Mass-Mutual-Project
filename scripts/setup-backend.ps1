<#
.SYNOPSIS
    Creates the backend virtual environment and installs dependencies.
#>

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$backendDir = Join-Path $repoRoot "apps\backend"

Push-Location $backendDir
try {
    if (-not (Test-Path ".venv")) {
        Write-Host "Creating virtual environment..."
        python -m venv .venv
    }

    Write-Host "Installing backend dependencies..."
    & ".venv\Scripts\python.exe" -m pip install --upgrade pip
    & ".venv\Scripts\python.exe" -m pip install -r requirements.txt

    if (-not (Test-Path ".env") -and (Test-Path ".env.example")) {
        Copy-Item ".env.example" ".env"
        Write-Host "Created apps/backend/.env from .env.example -- edit it with your local values."
    }

    Write-Host "Backend setup complete."
}
finally {
    Pop-Location
}
