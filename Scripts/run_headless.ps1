$ErrorActionPreference = "Stop"

Write-Host "Starting FireWizard3D in headless mode..."

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

if (-not (Test-Path ".\.venv\Scripts\Activate.ps1")) {
    Write-Error "Virtual environment not found at .\.venv\Scripts\Activate.ps1"
}
. .\.venv\Scripts\Activate.ps1

$env:PYTHONPATH = $ProjectRoot

# Assumes your main entry supports --headless
python -m app.main --headless

if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}