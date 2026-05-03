@echo off
REM Start script for the Knowledge Management API on Windows
REM This script uses --app-dir to properly resolve imports

setlocal enabledelayedexpansion

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0

REM Remove trailing backslash
set SCRIPT_DIR=%SCRIPT_DIR:~0,-1%

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
echo App directory: %SCRIPT_DIR%\src
echo Host: %HOST%
echo Port: %PORT%

REM Run uvicorn with --app-dir to resolve imports correctly
cd /d "%SCRIPT_DIR%"
uvicorn main:app --app-dir src --reload --host %HOST% --port %PORT%

endlocal
