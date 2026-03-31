param(
  [string]$TaskName = "BonGustoDailyBackup",
  [string]$ScriptPath = "C:\Users\sebas\Downloads\bongusto_django\run_daily_backup.ps1",
  [string]$StartTime = "03:00"
)

$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -File `"$ScriptPath`""
$trigger = New-ScheduledTaskTrigger -Daily -At $StartTime
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable

Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -Force
Write-Host "Tarea diaria creada: $TaskName a las $StartTime"
