param(
  [string]$RepoZipUrl = "https://github.com/shenguanwang/demo/archive/refs/heads/main.zip",
  [string]$InstallDir = "C:\overseas-lead-workbench",
  [int]$Port = 80,
  [string]$HostAddress = "0.0.0.0",
  [string]$AppUsername = "admin",
  [string]$AppPassword = "",
  [string]$GoogleMapsApiKey = "",
  [string]$AppAuthSecret = "",
  [int]$DiscoveryMaxConcurrency = 2
)

$ErrorActionPreference = "Stop"

function New-Secret([int]$Length = 32) {
  $bytes = New-Object byte[] $Length
  [System.Security.Cryptography.RandomNumberGenerator]::Fill($bytes)
  return [Convert]::ToBase64String($bytes).TrimEnd("=")
}

if (-not $AppPassword) {
  throw "AppPassword is required. Pass -AppPassword '<password>'."
}
if (-not $AppAuthSecret) {
  $AppAuthSecret = New-Secret 32
}

$pythonExe = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $pythonExe) {
  $installer = Join-Path $env:TEMP "python-3.12.4-amd64.exe"
  Invoke-WebRequest -Uri "https://www.python.org/ftp/python/3.12.4/python-3.12.4-amd64.exe" -OutFile $installer
  Start-Process -FilePath $installer -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1 Include_pip=1" -Wait
  $pythonExe = "C:\Program Files\Python312\python.exe"
}

New-Item -ItemType Directory -Force $InstallDir | Out-Null
New-Item -ItemType Directory -Force (Join-Path $InstallDir "data") | Out-Null

$zipPath = Join-Path $env:TEMP "overseas-lead-workbench-main.zip"
$extractRoot = Join-Path $env:TEMP ("overseas-lead-workbench-" + [guid]::NewGuid().ToString("N"))
Invoke-WebRequest -Uri $RepoZipUrl -OutFile $zipPath
Expand-Archive -Path $zipPath -DestinationPath $extractRoot -Force
$sourceDir = Get-ChildItem -Path $extractRoot -Directory | Select-Object -First 1
if (-not $sourceDir) {
  throw "Cannot find extracted source directory."
}

Get-ChildItem -Path $InstallDir -Force |
  Where-Object { $_.Name -notin @("data", "workbench-state.db") } |
  Remove-Item -Recurse -Force
Copy-Item -Path (Join-Path $sourceDir.FullName "*") -Destination $InstallDir -Recurse -Force

& $pythonExe -m pip install --upgrade pip
& $pythonExe -m pip install -r (Join-Path $InstallDir "requirements.txt")
& $pythonExe -m py_compile (Join-Path $InstallDir "server.py")

$runScript = Join-Path $InstallDir "run-server.ps1"
$statePath = Join-Path $InstallDir "data\workbench-state.db"
@"
`$env:LEAD_TOOL_HOST = "$HostAddress"
`$env:LEAD_TOOL_PORT = "$Port"
`$env:APP_USERNAME = "$AppUsername"
`$env:APP_PASSWORD = "$AppPassword"
`$env:APP_AUTH_SECRET = "$AppAuthSecret"
`$env:GOOGLE_MAPS_API_KEY = "$GoogleMapsApiKey"
`$env:STATE_DATABASE_PATH = "$statePath"
`$env:DISCOVERY_MAX_CONCURRENCY = "$DiscoveryMaxConcurrency"
`$env:NETWORK_DEFAULT_TIMEOUT = "12"
`$env:DISCOVERY_SEARCH_TIMEOUT = "18"
`$env:DISCOVERY_JOB_TIMEOUT_SECONDS = "900"
Set-Location "$InstallDir"
& "$pythonExe" "$InstallDir\server.py"
"@ | Set-Content -Path $runScript -Encoding UTF8

$taskName = "OverseasLeadWorkbench"
if (Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue) {
  Stop-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
  Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
}
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$runScript`""
$trigger = New-ScheduledTaskTrigger -AtStartup
$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -RunLevel Highest
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Principal $principal | Out-Null

New-NetFirewallRule -DisplayName "Overseas Lead Workbench HTTP $Port" -Direction Inbound -Protocol TCP -LocalPort $Port -Action Allow -ErrorAction SilentlyContinue | Out-Null
New-NetFirewallRule -DisplayName "Overseas Lead Workbench App 8815" -Direction Inbound -Protocol TCP -LocalPort 8815 -Action Allow -ErrorAction SilentlyContinue | Out-Null

Start-ScheduledTask -TaskName $taskName
Start-Sleep -Seconds 5

$healthUrl = "http://127.0.0.1:$Port/health"
try {
  $health = Invoke-WebRequest -Uri $healthUrl -UseBasicParsing -TimeoutSec 15
  Write-Host "Deployment OK: $($health.Content)"
} catch {
  Write-Host "Deployment started, but health check failed: $($_.Exception.Message)"
  throw
}

Write-Host "Public URL: http://$((Invoke-WebRequest -Uri 'https://api.ipify.org' -UseBasicParsing -TimeoutSec 10).Content)/"
