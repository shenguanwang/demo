$ErrorActionPreference = "Stop"

$source = Join-Path $PSScriptRoot "official-site"
$target = "C:\sites\yiming-auto"

if (-not (Test-Path (Join-Path $source "index.html"))) {
  throw "Official site source is missing: $source"
}

New-Item -ItemType Directory -Force -Path $target | Out-Null
Copy-Item -Path (Join-Path $source "*") -Destination $target -Recurse -Force

Write-Host "Official site synced to $target"
