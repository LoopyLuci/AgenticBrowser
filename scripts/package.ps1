param(
  [string]$Src = "agentic-browser-extension/dist",
  [string]$Dest = "release/agenticbrowser-extension-chrome.zip"
)

if (-not (Test-Path $Src)) {
  Write-Error "Missing extension dist: $Src"
  exit 1
}

$destDir = Split-Path -Parent $Dest
if (-not (Test-Path $destDir)) {
  New-Item -ItemType Directory -Path $destDir | Out-Null
}

if (Test-Path $Dest) {
  Remove-Item $Dest -Force
}

Compress-Archive -Path "$Src/*" -DestinationPath $Dest -Force
Write-Host "Packaged extension: $Dest"
