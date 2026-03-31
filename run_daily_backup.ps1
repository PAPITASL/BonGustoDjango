param(
  [string]$ProjectDir = "C:\Users\sebas\Downloads\bongusto_django\bongusto_django",
  [string]$PythonPath = "C:\Users\sebas\Downloads\bongusto_django\.venv\Scripts\python.exe",
  [string]$BackupDir = "C:\Users\sebas\Downloads\bongusto_django\backups",
  [int]$Keep = 7
)

Set-Location $ProjectDir
& $PythonPath manage.py backup_data --output-dir $BackupDir --keep $Keep
