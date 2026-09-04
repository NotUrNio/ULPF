@echo off
setlocal enabledelayedexpansion
title Create ULPF Desktop Shortcuts
color 0A
cd /d "%~dp0"
cls
echo ======================================================================
echo           Creating ULPF Desktop Shortcuts...
echo ======================================================================
echo.

set "ROOT_DIR=%~dp0"
if "%ROOT_DIR:~-1%"=="\" set "ROOT_DIR=%ROOT_DIR:~0,-1%"

powershell -NoProfile -ExecutionPolicy Bypass -Command "$ws = New-Object -ComObject WScript.Shell; $desktop = [System.Environment]::GetFolderPath('Desktop'); $root = $env:ROOT_DIR; $icon = [System.IO.Path]::Combine($root, 'packaging\windows\ulpf_icon.ico'); $startLink = $ws.CreateShortcut([System.IO.Path]::Combine($desktop, 'ULPF Dashboard.lnk')); $startLink.TargetPath = [System.IO.Path]::Combine($root, 'Start_Dashboard_Background.vbs'); $startLink.WorkingDirectory = $root; $startLink.Description = 'Universal Log Pre-processing Framework Dashboard'; if (Test-Path $icon) { $startLink.IconLocation = $icon; }; $startLink.Save(); Write-Host '[+] Successfully created: ' -NoNewline -ForegroundColor Green; Write-Host ([System.IO.Path]::Combine($desktop, 'ULPF Dashboard.lnk')) -ForegroundColor Cyan; $stopLink = $ws.CreateShortcut([System.IO.Path]::Combine($desktop, 'Stop ULPF Dashboard.lnk')); $stopLink.TargetPath = [System.IO.Path]::Combine($root, 'Stop_Dashboard.bat'); $stopLink.WorkingDirectory = $root; $stopLink.Description = 'Stop running ULPF Dashboard Server'; if (Test-Path $icon) { $stopLink.IconLocation = $icon; }; $stopLink.Save(); Write-Host '[+] Successfully created: ' -NoNewline -ForegroundColor Green; Write-Host ([System.IO.Path]::Combine($desktop, 'Stop ULPF Dashboard.lnk')) -ForegroundColor Cyan;"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ======================================================================
    echo   Desktop shortcuts created successfully!
    echo   You can now double-click 'ULPF Dashboard' on your desktop.
    echo ======================================================================
) else (
    echo.
    echo [ERROR] Failed to create desktop shortcuts.
)

echo.
pause
