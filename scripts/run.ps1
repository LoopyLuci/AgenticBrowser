# AgenticBrowser Windows startup helper
param(
    [switch]$SkipExtension
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$extensionDir = Join-Path $root 'agentic-browser-extension'
$extensionPath = Join-Path $extensionDir 'dist'

$env:AGENTIC_BROWSER_ROOT = $root

if (-not $SkipExtension) {
    $brave = 'C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe'
    if (Test-Path $brave) {
        Start-Process -FilePath $brave -ArgumentList "--load-extension=`"$extensionPath`""
    } else {
        Write-Warning "Brave not found at $brave"
    }
}
