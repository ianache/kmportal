@echo off
REM Start script for the Knowledge Management API on Windows
REM This script ensures PYTHONPATH is set correctly for imports

setlocal enabledelayedexpansion

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0

REM Remove trailing backslash
set SCRIPT_DIR=%SCRIPT_DIR:~0,-1%

REM Set PYTHONPATH to include the src directory
set PYTHONPATH=%SCRIPT_DIR%;%PYTHONPATH%

REM Default values
if "%~1"=="" (
    set HOST=0.0.0.0
) else (
    set HOST=%~1
)

if "%~2"=="" (
    set PORT=8000
) else (
    set PORT=%~2
)

echo Starting Knowledge Management API...
echo PYTHONPATH: %PYTHONPATH%
echo Host: %HOST%
echo Port: %PORT%

REM Run uvicorn
cd /d "%SCRIPT_DIR%"
uvicorn src.main:app --reload --host %HOST% --port %PORT%

endlocal
