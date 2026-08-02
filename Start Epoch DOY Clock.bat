@echo off
cd /d "%~dp0"

where pythonw.exe >nul 2>nul
if %errorlevel%==0 (
    start "" pythonw.exe "%~dp0epoch_doy_clock.py"
    exit /b
)

where pyw.exe >nul 2>nul
if %errorlevel%==0 (
    start "" pyw.exe -3 "%~dp0epoch_doy_clock.py"
    exit /b
)

where py.exe >nul 2>nul
if %errorlevel%==0 (
    start "" py.exe -3w "%~dp0epoch_doy_clock.py"
    exit /b
)

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Start Epoch DOY Clock.ps1"
