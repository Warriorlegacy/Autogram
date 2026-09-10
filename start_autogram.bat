@echo off
title Autogram — Autonomous Instagram Engine (7x Daily)
cd /d "%~dp0"

echo =======================================================
echo   Starting Autogram Engine + 7x Daily Scheduler + Tunnel
echo =======================================================
echo.

echo [1/3] Starting Dashboard API server (port 5050)...
start "Autogram Dashboard" /b .venv\Scripts\python.exe dashboard_api.py

timeout /t 2 >nul

echo [2/3] Starting Ngrok Public Tunnel...
start "Ngrok Tunnel" /b "%LOCALAPPDATA%\Microsoft\WinGet\Links\ngrok.exe" http 5050

timeout /t 2 >nul

echo [3/3] Starting Autonomous 7x Daily Publishing Scheduler...
start "Autogram 7x Scheduler" /b .venv\Scripts\python.exe orchestrator.py --schedule

timeout /t 2 >nul
echo.
echo =======================================================
echo   All systems live! Opening your Dashboard...
echo   Local Dashboard:  http://localhost:5050/dashboard
echo   7 Posting Slots:  08:00, 10:30, 13:00, 15:30, 18:00, 20:30, 22:30 IST
echo =======================================================
start http://localhost:5050/dashboard
