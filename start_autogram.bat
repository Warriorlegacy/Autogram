@echo off
title Autogram — Autonomous Instagram Engine
cd /d "%~dp0"

echo =======================================================
echo   Starting Autogram Engine + Ngrok Tunnel
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
echo   All systems live! Opening your Dashboard...
echo   Local URL:  http://localhost:5050/dashboard
echo =======================================================
start http://localhost:5050/dashboard
