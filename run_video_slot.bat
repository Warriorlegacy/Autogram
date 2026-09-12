@echo off
REM Single local video slot: ensure MPT render server, then render + dual-publish.
REM Usage: run_video_slot.bat "Pillar Name"  (topic auto-acquired)
set PILLAR=%~1
if "%PILLAR%"=="" set PILLAR=AI Tool Breakdown
cd /d D:\Autogram
call D:\Autogram\ensure_mpt.bat
C:\Python314\python.exe D:\Autogram\orchestrator.py --video --run-all --pillar "%PILLAR%"
