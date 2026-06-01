param(
  [int]$Vus = 20,
  [string]$Duration = "30s",
  [int[]]$PreferredPorts = @(8010, 8011, 8012),
  [switch]$KeepServerRunning
)

$ErrorActionPreference = "Stop"

$root = "C:\Users\sebas\Downloads\bongusto_django"
$projectDir = Join-Path $root "bongusto_django"
$pythonPath = Join-Path $root ".venv\Scripts\python.exe"
$k6Path = Join-Path $projectDir "k6\k6.exe"
$loadTestPath = Join-Path $projectDir "load_test.js"
$serverOut = Join-Path $projectDir "runserver.out.log"
$serverErr = Join-Path $projectDir "runserver.err.log"

function Test-HttpOk {
  param([string]$Url)

  try {
    $response = Invoke-WebRequest -UseBasicParsing $Url -TimeoutSec 2
    return $response.StatusCode -eq 200
  } catch {
    return $false
  }
}

function Get-FreePort {
  param([int[]]$Ports)

  foreach ($port in $Ports) {
    $connection = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if (-not $connection) {
      return $port
    }
  }

  throw "No hay puertos libres en la lista: $($Ports -join ', ')"
}

function Get-ReusablePort {
  param([int[]]$Ports)

  foreach ($port in $Ports) {
    if (Test-HttpOk "http://127.0.0.1:$port/ping/") {
      return $port
    }
  }

  return $null
}

if (-not (Test-Path $pythonPath)) {
  throw "No se encontró Python en $pythonPath"
}

if (-not (Test-Path $k6Path)) {
  throw "No se encontró k6 en $k6Path"
}

$selectedPort = Get-ReusablePort -Ports $PreferredPorts
$startedServer = $false
$serverProcess = $null

if (-not $selectedPort) {
  $selectedPort = Get-FreePort -Ports $PreferredPorts

  Remove-Item -LiteralPath $serverOut, $serverErr -ErrorAction SilentlyContinue
  $serverProcess = Start-Process `
    -FilePath $pythonPath `
    -ArgumentList "manage.py", "runserver", "127.0.0.1:$selectedPort", "--noreload" `
    -WorkingDirectory $projectDir `
    -RedirectStandardOutput $serverOut `
    -RedirectStandardError $serverErr `
    -WindowStyle Hidden `
    -PassThru

  for ($i = 0; $i -lt 20; $i++) {
    Start-Sleep -Seconds 1

    if ($serverProcess.HasExited) {
      $outLog = if (Test-Path $serverOut) { Get-Content $serverOut -Raw } else { "" }
      $errLog = if (Test-Path $serverErr) { Get-Content $serverErr -Raw } else { "" }
      throw "Django no logró iniciar en $selectedPort.`nOUT:`n$outLog`nERR:`n$errLog"
    }

    if (Test-HttpOk "http://127.0.0.1:$selectedPort/ping/") {
      $startedServer = $true
      break
    }
  }

  if (-not $startedServer) {
    throw "Django no respondió en /ping/ sobre el puerto $selectedPort"
  }
}

$env:BASE_URL = "http://127.0.0.1:$selectedPort"
$env:VUS = "$Vus"
$env:DURATION = $Duration

Write-Host "Usando BASE_URL=$env:BASE_URL"
Write-Host "Ejecutando k6 con VUS=$env:VUS DURATION=$env:DURATION"

try {
  & $k6Path run $loadTestPath
} finally {
  if ($startedServer -and -not $KeepServerRunning -and $serverProcess -and -not $serverProcess.HasExited) {
    Stop-Process -Id $serverProcess.Id -Force
  }
}
