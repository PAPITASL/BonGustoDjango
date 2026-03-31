$adb = "C:\Users\sebas\AppData\Local\Android\Sdk\platform-tools\adb.exe"
$devicesOutput = & $adb devices
$deviceId = $null

foreach ($line in $devicesOutput) {
  if ($line -match "^\s*([A-Za-z0-9:_-]+)\s+device\s*$") {
    $deviceId = $matches[1]
    break
  }
}

if (-not $deviceId) {
  Write-Error "No hay ningun dispositivo Android disponible en adb."
  exit 1
}

Write-Host "Usando dispositivo: $deviceId"
& $adb -s $deviceId reverse tcp:8080 tcp:8080

Set-Location "C:\Users\sebas\Downloads\bongusto_django\clientes"
flutter run -d $deviceId
