@echo off
setlocal
cd /d "%~dp0"

where py.exe >nul 2>nul
if %errorlevel%==0 (
    set "PY=py -3"
) else (
    where python.exe >nul 2>nul
    if %errorlevel%==0 (
        set "PY=python"
    ) else (
        echo ERROR: Python 3 was not found.
        pause
        exit /b 1
    )
)

%PY% -m pip install --user --upgrade pyinstaller
if errorlevel 1 (
    echo ERROR: Could not install/update PyInstaller.
    pause
    exit /b 1
)

%PY% -m PyInstaller ^
    --noconfirm ^
    --clean ^
    --onefile ^
    --windowed ^
    --name "Epoch DOY Clock" ^
    epoch_doy_clock.py

if errorlevel 1 (
    echo ERROR: Build failed.
    pause
    exit /b 1
)

explorer.exe "%CD%\dist"
pause
