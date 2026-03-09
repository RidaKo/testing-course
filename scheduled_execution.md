## Exercise 4.2 Scheduled Execution

Implemented scheduling options:

1. GitHub Actions schedule  
- File: `.github/workflows/scheduled-ui-tests.yml`  
- Trigger: daily at `05:30 UTC` (`cron: 30 5 * * *`)  
- Suite: `pytest -m "exercise_group_1"`  
- Proof artifact: `scheduled-ui-test-report` (JUnit XML upload)

2. Local Windows Task Scheduler scripts  
- Run script: `scripts/run_scheduled_suite.ps1`  
- Registration script: `scripts/register_daily_task.ps1`  
- Daily trigger default: `08:00` local time  
- Local proof files: `reports/scheduled-ui-<timestamp>.xml` and `reports/scheduled-ui-<timestamp>.log`

### Quick start (local)

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\register_daily_task.ps1
```

To manually execute once and generate proof files:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run_scheduled_suite.ps1
```

### Proof generated in this workspace

- Date/time: March 9, 2026 at 18:20 (Europe/Kiev)
- Log file: `reports/scheduled-ui-20260309-181935.log`
- JUnit XML: `reports/scheduled-ui-20260309-181935.xml`
