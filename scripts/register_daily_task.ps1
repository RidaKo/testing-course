param(
    [string]$TaskName = "TestingCourse-ExerciseGroup1",
    [string]$RunAt = "08:00"
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$runnerScript = Join-Path $projectRoot "scripts\\run_scheduled_suite.ps1"

$action = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$runnerScript`""
$trigger = New-ScheduledTaskTrigger -Daily -At $RunAt

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $action `
    -Trigger $trigger `
    -Description "Runs Exercise Group 1 automation suite daily" `
    -Force | Out-Null

Write-Host "Scheduled task '$TaskName' is registered and will run daily at $RunAt."
