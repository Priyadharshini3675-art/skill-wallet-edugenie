@echo off
setlocal EnableExtensions DisableDelayedExpansion
cd /d "%~dp0"
title EduGenie - Gemini AI
color 0B
echo ================================================
echo          EduGenie - Real Gemini AI
echo ================================================
if exist ".venv\Scripts\python.exe" goto ready
where py >nul 2>nul
if not errorlevel 1 (
  set "PYCMD=py -3"
  goto create
)
where python >nul 2>nul
if not errorlevel 1 (
  set "PYCMD=python"
  goto create
)
echo [ERROR] Install Python 3.10+ with Add to PATH enabled.
pause
exit /b 1
:create
%PYCMD% -m venv .venv
if errorlevel 1 goto fail
:ready
echo [1/3] Checking dependencies...
".venv\Scripts\python.exe" -c "import fastapi,uvicorn,google.genai,dotenv,jinja2,httpx"
if errorlevel 1 (
  ".venv\Scripts\python.exe" -m pip install -r requirements.txt
  if errorlevel 1 goto fail
)
echo [2/3] Gemini configuration and API connection test...
".venv\Scripts\python.exe" config_setup.py
if errorlevel 1 goto fail
echo [3/3] Starting http://127.0.0.1:8000
start "" "http://127.0.0.1:8000"
".venv\Scripts\python.exe" -m uvicorn main:app --host 127.0.0.1 --port 8000
if errorlevel 1 goto fail
exit /b 0
:fail
echo Setup or server startup failed. Ensure port 8000 is free.
pause
exit /b 1
