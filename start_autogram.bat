@echo off
title Autogram - Dashboard (Manual Control)
cd /d "%~dp0"

echo =======================================================
echo   Autogram Dashboard - manual control + monitoring
echo   NOTE: Scheduled publishing runs in the CLOUD
echo   (cron-job.org -^> GitHub Actions). This PC never
echo   auto-publishes, so cloud + local can never double-post.
echo   Use the Dashboard buttons or CLI for manual drops.
echo =======================================================
echo.

echo [1/2] Starting Dashboard API server (port 5050)...
start "Autogram Dashboard" /b .venv\Scripts\python.exe dashboard_api.py

timeout /t 2 >nul

echo [2/2] Starting Ngrok Public Tunnel...
start "Ngrok Tunnel" /b "%LOCALAPPDATA%\Microsoft\WinGet\Links\ngrok.exe" http 5050

timeout /t 2 >nul
echo.
echo =======================================================
echo   Local Dashboard:  http://localhost:5050/dashboard
echo   Cloud cadence:    7 carousels + 7 stories + 4 reels/day
echo   Local reels:      run_video_slot.bat "Pillar" (manual top-ups)
echo =======================================================
start http://localhost:5050/dashboard
