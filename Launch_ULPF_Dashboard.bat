@echo off
setlocal enabledelayedexpansion
title ULPF Operations Dashboard
color 0B
cd /d "%~dp0"

:: Detect Python
set "PYTHON_EXE="
where python >nul 2>&1
if %ERRORLEVEL% EQU 0 set "PYTHON_EXE=python"
if not defined PYTHON_EXE (
    where py >nul 2>&1
    if !ERRORLEVEL! EQU 0 set "PYTHON_EXE=py"
)
if not defined PYTHON_EXE (
    if exist "%LOCALAPPDATA%\Programs\Python\Python314\python.exe" (
        set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python314\python.exe"
    ) else if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
        set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    ) else if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
        set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
    )
)

if not defined PYTHON_EXE (
    echo [ERROR] Python was not found in your system.
    echo Please install Python 3.11+ from https://www.python.org/
    echo and ensure 'Add Python to PATH' is checked.
    echo.
    pause
    exit /b 1
)

:: Launch dashboard with auto-browser opening in persistent background mode
!PYTHON_EXE! -m ulpf.cli dashboard --background --open-browser --port 7000 --output-dir output
exit /b 0
