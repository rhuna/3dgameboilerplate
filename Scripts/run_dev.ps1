param(
    [string]$Scenario = "ember_trial"
)
$ErrorActionPreference = "Stop"


Write-Host "Starting FireWizard3D (scenario: $Scenario)"

$venvPath = ".\.venv\Scripts\Activate.ps1"

if (!(Test-Path $venvPath)) {
    Write-Host "Virtual environment not found. Creating one..."
    python -m venv .venv
}

. $venvPath
$env:PYTHONPATH = "."



python -m app.main --scenario $Scenario

