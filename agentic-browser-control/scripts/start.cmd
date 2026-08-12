@echo off
setlocal

set PORT=%1
if "%PORT%"=="" set PORT=8766

for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":%PORT% " ^| findstr LISTENING') do (
  echo Killing stale PID %%a on port %PORT%
  taskkill /F /PID %%a >nul 2>&1
  ping 127.0.0.1 -n 2 >nul
)

for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8766 " ^| findstr LISTENING') do (
  if /I not "%PORT%"=="8766" (
    echo Killing stale PID %%a on port 8766
    taskkill /F /PID %%a >nul 2>&1
    ping 127.0.0.1 -n 2 >nul
  )
)

set AGENTIC_CONTROL_SECRET=demo
cd /d %~dp0..
npx tsx src/server.ts
