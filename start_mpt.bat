@echo off
REM Starts the local MoneyPrinterTurbo render server ($0 video engine).
REM Autogram's --reel pipeline calls http://127.0.0.1:8080/api/v1/videos
REM Keep this window open while rendering Reels. Press Ctrl+C to stop.
cd /d D:\MoneyPrinterTurbo
if exist .venv\Scripts\python.exe (
  .venv\Scripts\python.exe main.py
) else (
  python main.py
)
pause
