$ErrorActionPreference = "Stop"

Write-Host "Running test suite..."

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

if (-not (Test-Path ".\.venv\Scripts\Activate.ps1")) {
    Write-Error "Virtual environment not found at .\.venv\Scripts\Activate.ps1"
}
. .\.venv\Scripts\Activate.ps1

$env:PYTHONPATH = $ProjectRoot

pytest -v --maxfail=1 --disable-warnings

if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}