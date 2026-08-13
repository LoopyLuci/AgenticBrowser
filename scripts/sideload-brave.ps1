<#
.SYNOPSIS
Auto-elevating sideload install for AgenticBrowser into Brave.
#>

param(
    [string]$ExtensionDir = "$PSScriptRoot\..\agentic-browser-extension\dist",
    [string]$BraveExe = "$Env:ProgramFiles\BraveSoftware\Brave-Browser\Application\brave.exe"
)

$ErrorActionPreference = 'Stop'

function Test-Admin {
    $current = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($current)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

if (-not (Test-Admin)) {
    Write-Host "Requesting elevation..."
    $args = @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $MyInvocation.MyCommand.Path)
    if ($PSBoundParameters.ContainsKey('ExtensionDir')) {
        $args += @("-ExtensionDir", $ExtensionDir)
    }
    if ($PSBoundParameters.ContainsKey('BraveExe')) {
        $args += @("-BraveExe", $BraveExe)
    }
    Start-Process -FilePath "powershell.exe" -ArgumentList $args -Verb RunAs
    exit 0
}

Write-Host "Running elevated."

if (-not (Test-Path $BraveExe)) {
    Write-Error "Brave not found at: $BraveExe"
    exit 1
}

$resolvedBrave = (Resolve-Path $BraveExe).Path
Write-Host "Brave: $resolvedBrave"

if (-not (Test-Path $ExtensionDir)) {
    Write-Error "Extension dir not found: $ExtensionDir"
    exit 1
}

$resolvedExt = (Resolve-Path $ExtensionDir).Path
Write-Host "Extension: $resolvedExt"

# Close existing Brave instances to ensure clean load.
$braveProcs = Get-Process -Name "brave" -ErrorAction SilentlyContinue
if ($braveProcs) {
    Write-Host "Closing existing Brave instances..."
    $braveProcs | Stop-Process -Force
    Start-Sleep -Seconds 2
}

Write-Host "Launching Brave with sideloaded extension..."
Start-Process -FilePath $resolvedBrave -ArgumentList "--load-extension=`"$resolvedExt`""

Write-Host "Done. Open brave://extensions/ to verify AgenticBrowser is enabled."
