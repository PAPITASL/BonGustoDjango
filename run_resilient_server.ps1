param(
  [string]$ProjectDir = "C:\Users\sebas\Downloads\bongusto_django\bongusto_django",
  [string]$PythonPath = "C:\Users\sebas\Downloads\bongusto_django\.venv\Scripts\python.exe",
  [int]$Port = 8080,
  [int]$RestartDelaySeconds = 5
)

Set-Location $ProjectDir

while ($true) {
  & $PythonPath -m daphne -b 0.0.0.0 -p $Port bongusto.infrastructure.asgi:application
  Write-Host "Servidor detenido. Reiniciando en $RestartDelaySeconds segundos..."
  Start-Sleep -Seconds $RestartDelaySeconds
}
