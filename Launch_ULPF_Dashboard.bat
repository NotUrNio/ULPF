@echo off
title ULPF Operations Dashboard Launcher
color 0B
cls
echo ======================================================================
echo           Universal Log Pre-processing Framework (ULPF)
echo ======================================================================
echo.

if exist "dist\ulpf-dashboard.exe" (
    echo [*] Launching standalone ULPF Dashboard executable...
    dist\ulpf-dashboard.exe --port 8000 --output-dir output
    goto :done
)

echo [*] Checking Python environment...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Neither standalone executable (dist\ulpf-dashboard.exe) nor Python is available.
    echo Please run packaging\windows\build_exe.py or install Python 3.11+.
    pause
    exit /b 1
)

echo [*] Initializing sample log ingestion...
python -m ulpf.cli ingest --input ulpf/sample_logs/ --output output/ >nul 2>&1

echo [*] Starting ULPF Dashboard Server on port 8000...
echo [INFO] Press Ctrl+C in this window to stop the server.
echo.
python -m ulpf.dashboard.app --port 8000 --output-dir output

:done
pause
