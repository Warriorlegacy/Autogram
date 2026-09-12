@echo off
title Autogram — Autonomous Instagram Engine (7x Daily)
cd /d "%~dp0"

echo =======================================================
echo   Starting Autogram Engine + 24x Daily Scheduler (10 Videos, 7 Posts, 7 Stories)
echo =======================================================
echo.

echo [1/3] Starting Dashboard API server (port 5050)...
start "Autogram Dashboard" /b .venv\Scripts\python.exe dashboard_api.py

timeout /t 2 >nul

echo [2/3] Starting Ngrok Public Tunnel...
start "Ngrok Tunnel" /b "%LOCALAPPDATA%\Microsoft\WinGet\Links\ngrok.exe" http 5050

timeout /t 2 >nul

echo [3/3] Starting Autonomous 24x Daily Publishing Scheduler...
start "Autogram 24x Scheduler" /b .venv\Scripts\python.exe orchestrator.py --schedule

timeout /t 2 >nul
echo.
echo =======================================================
echo   All systems live! Opening your Dashboard...
echo   Local Dashboard:  http://localhost:5050/dashboard
echo   10 Video Slots:   08:00, 09:45, 11:00, 12:00, 13:45, 15:00, 16:30, 18:30, 20:00, 22:00 IST
echo   7 Carousel Slots: 08:00, 10:30, 13:00, 15:30, 18:00, 20:30, 22:30 IST
echo   7 Story Slots:    09:00, 11:30, 14:00, 16:30, 19:00, 21:30, 23:30 IST
echo =======================================================
start http://localhost:5050/dashboard
