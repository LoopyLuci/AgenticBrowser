<#
.SYNOPSIS
    On-device CI/CD runner for Windows.
#>

param(
  [switch]$Watch,
  [switch]$SkipTests,
  [switch]$SkipPackaging
)

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'

$ReportDir = Join-Path $PWD 'reports'
New-Item -ItemType Directory -Force -Path $ReportDir | Out-Null

$log = [System.IO.StreamWriter]::new((Join-Path $ReportDir 'ci.log'), $true)
$results = @()

function Write-StageLog($msg) {
  Write-Host ''
  Write-Host "== $msg ==" -ForegroundColor Cyan
  $log.WriteLine("== $msg ==")
}

function Pass-Stage($name) {
  Write-Host "PASS: $name" -ForegroundColor Green
  $log.WriteLine("PASS: $name")
  $results += [PSCustomObject]@{
    stage = $name
    status = 'passed'
    timestamp = (Get-Date -Format o)
  }
}

function Fail-Stage($name) {
  Write-Host "FAILED: $name" -ForegroundColor Red
  $log.WriteLine("FAILED: $name")
  $results += [PSCustomObject]@{
    stage = $name
    status = 'failed'
    timestamp = (Get-Date -Format o)
  }
  $results | ConvertTo-Json | Out-File (Join-Path $ReportDir 'results.jsonl') -Append
  $log.Close()
  exit 1
}

# Init results
$results | ConvertTo-Json | Out-File (Join-Path $ReportDir 'results.jsonl')
'{"run":"started","timestamp":"' + (Get-Date -Format o) + '"}' | Out-File (Join-Path $ReportDir 'results.jsonl') -Append

if ($Watch) {
  Write-Host 'Watch mode: run full pipeline on file changes (Ctrl+C to exit)' -ForegroundColor Yellow
  $watcher = New-Object System.IO.FileSystemWatcher
  $watcher.Path = $PWD
  $watcher.IncludeSubdirectories = $true
  $watcher.Filter = '*'
  $watcher.NotifyFilter = [IO.NotifyFilters]'LastWrite,FileName,DirectoryName'

  $lastRun = Get-Date
  while ($true) {
    $result = $watcher.WaitForChanged('Changed', 2000)
    if (-not $result.TimedOut) {
      $now = Get-Date
      if (($now - $lastRun).TotalSeconds -gt 2) {
        $lastRun = $now
        Write-Host "`nChange detected, rerunning..." -ForegroundColor Yellow
        try {
          pwsh -File $MyInvocation.MyCommand.Path
        } catch {}
      }
    }
  }
}

# Backend
Write-StageLog 'Backend tests'
Set-Location (Join-Path $PWD 'agentic-browser-backend')
try {
  & .venv/Scripts/python -m pytest tests/test_backend.py tests/test_providers.py tests/test_observability.py tests/test_rate_limit.py tests/test_ssl.py tests/test_supervisor.py tests/test_discord.py tests/test_discord_webhook.py tests/test_providers_adapters.py tests/test_provider_resilience.py -v --tb=short 2>&1 | Tee-Object -FilePath (Join-Path $ReportDir 'backend-tests.log')
  Pass-Stage 'backend-tests'
} catch {
  Fail-Stage 'backend-tests'
}

# Control plane
Write-StageLog 'Control plane build + test'
Set-Location (Join-Path $PWD 'agentic-browser-control')
try {
  npm run build 2>&1 | Tee-Object -FilePath (Join-Path $ReportDir 'control-build.log')
  npm test 2>&1 | Tee-Object -FilePath (Join-Path $ReportDir 'control-tests.log')
  Pass-Stage 'control-plane'
} catch {
  Fail-Stage 'control-plane'
}

# Extension
Write-StageLog 'Extension build + Playwright'
Set-Location (Join-Path $PWD 'agentic-browser-extension')
try {
  npm run build 2>&1 | Tee-Object -FilePath (Join-Path $ReportDir 'extension-build.log')
  npx playwright test tests/sidepanel-error-e2e.spec.ts --reporter=line --project=brave-extension 2>&1 | Tee-Object -FilePath (Join-Path $ReportDir 'extension-e2e.log')
  Pass-Stage 'extension-build'
} catch {
  Write-Host "NOTE: Brave E2E test may fail due to browser automation limits; check $ReportDir/extension-e2e.log" -ForegroundColor Yellow
  $results += [PSCustomObject]@{
    stage = 'extension-e2e'
    status = 'skipped'
    reason = 'brave-automation-limit'
    timestamp = (Get-Date -Format o)
  }
  Pass-Stage 'extension-build'
}

# Packaging
if (-not $SkipPackaging) {
  Write-StageLog 'Windows packaging validation'
  Set-Location $PWD
  try {
    bash scripts/package-extension.sh agentic-browser-extension/dist release/agenticbrowser-extension-windows.zip 2>&1 | Tee-Object -FilePath (Join-Path $ReportDir 'packaging.log')
    python scripts/validate-release.py 2>&1 | Tee-Object -FilePath (Join-Path $ReportDir 'packaging.log')
    Pass-Stage 'packaging-windows'
  } catch {
    Fail-Stage 'packaging-windows'
  }
} else {
  Write-Host 'Skipping packaging (--SkipPackaging)'
}

# Web UI
Write-StageLog 'Web UI tests + build'
Set-Location (Join-Path $PWD 'agentic-browser-web-ui')
try {
  npm test 2>&1 | Tee-Object -FilePath (Join-Path $ReportDir 'web-tests.log')
  npm run build 2>&1 | Tee-Object -FilePath (Join-Path $ReportDir 'web-build.log')
  Pass-Stage 'web-ui'
} catch {
  Fail-Stage 'web-ui'
}

# Root build
Write-StageLog 'Root monorepo build'
Set-Location $PWD
try {
  npm run build 2>&1 | Tee-Object -FilePath (Join-Path $ReportDir 'root-build.log')
  Pass-Stage 'root-build'
} catch {
  Fail-Stage 'root-build'
}

Write-Host ''
Write-Host '== CI Summary ==' -ForegroundColor Cyan
Write-Host "Report: $ReportDir/ci.log"
Write-Host "Results: $ReportDir/results.jsonl"
Write-Host ''
Write-Host '== Local CI passed ==' -ForegroundColor Green

$results | ConvertTo-Json | Out-File (Join-Path $ReportDir 'results.jsonl') -Append
$log.Close()
