param(
  [string]$Port = "8766",
  [string]$ControlSecret = "demo",
  [string]$BackendBase = "http://127.0.0.1:8123"
)

$ErrorActionPreference = "Stop"
$script:ControlPid = $null

function Stop-ControlPort {
  param([int]$Port)
  $listeners = @(Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue)
  foreach ($l in $listeners) {
    if ($l -and $l.OwningProcess -gt 0) {
      Write-Host "Killing stale PID $($l.OwningProcess) on port $Port"
      try { Stop-Process -Id $l.OwningProcess -Force -ErrorAction Stop } catch { }
      Start-Sleep -Seconds 1
    }
  }
}

Stop-ControlPort -Port ([int]$Port)
Stop-ControlPort -Port 8766

$env:AGENTIC_CONTROL_SECRET = $ControlSecret
$env:AGENTIC_BACKEND = $BackendBase
$script:ControlPid = Start-Process -FilePath "npx" -ArgumentList "tsx","src/server.ts" -PassThru -NoNewWindow -Wait:$false -WorkingDirectory $PSScriptRoot\..
try {
  $url = "http://localhost:$Port/health"
  $time = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()
  while ([DateTimeOffset]::UtcNow.ToUnixTimeSeconds() - $time -lt 20) {
    try {
      $r = Invoke-WebRequest -Uri $url -UseBasicParsing -ErrorAction Stop
      if ($r.StatusCode -eq 200) {
        Write-Host "Control server on http://localhost:$Port"
        Write-Host "Press Ctrl+C to stop."
        while ($true) { Start-Sleep -Seconds 5 }
      }
    } catch {
      Start-Sleep -Milliseconds 250
    }
  }
  throw "Control server did not become ready within timeout"
} finally {
  if ($script:ControlPid -and !$script:ControlPid.HasExited) {
    Stop-Process -Id $script:ControlPid.Id -Force -ErrorAction SilentlyContinue
  }
}
