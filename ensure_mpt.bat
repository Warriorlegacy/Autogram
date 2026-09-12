@echo off
REM Ensures the local MoneyPrinterTurbo render server is up ($0 video engine).
REM Starts it in the background if :8080 is not responding. Safe to run often.
curl -s -o nul -m 5 http://127.0.0.1:8080/docs
if %errorlevel% neq 0 (
  echo [ensure_mpt] MPT down - starting server...
  start "" /min D:\MoneyPrinterTurbo\.venv\Scripts\python.exe D:\MoneyPrinterTurbo\main.py
  timeout /t 25 /nobreak >nul
) else (
  echo [ensure_mpt] MPT already running.
)
