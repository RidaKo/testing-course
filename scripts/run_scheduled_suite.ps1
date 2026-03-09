param(
    [string]$PythonPath = ".\\.venv\\Scripts\\python.exe",
    [string]$ReportDir = ".\\reports"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $ReportDir)) {
    New-Item -ItemType Directory -Path $ReportDir | Out-Null
}

$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$xmlReport = Join-Path $ReportDir "scheduled-ui-$timestamp.xml"
$logFile = Join-Path $ReportDir "scheduled-ui-$timestamp.log"

$command = "$PythonPath -m pytest -m `"exercise_group_1`" --browser chromium --junitxml `"$xmlReport`""

Write-Host "Running: $command"
Invoke-Expression "$command *>&1 | Tee-Object -FilePath `"$logFile`""

Write-Host "JUnit report: $xmlReport"
Write-Host "Execution log: $logFile"
