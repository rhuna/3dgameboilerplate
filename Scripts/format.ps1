$ErrorActionPreference = "Stop"

Write-Host "Formatting project..."

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

if (-not (Test-Path ".\.venv\Scripts\Activate.ps1")) {
    Write-Error "Virtual environment not found at .\.venv\Scripts\Activate.ps1"
}
. .\.venv\Scripts\Activate.ps1

$env:PYTHONPATH = $ProjectRoot

black .
ruff check . --fix

if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}