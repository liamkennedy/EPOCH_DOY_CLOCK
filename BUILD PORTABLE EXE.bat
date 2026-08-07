@echo off
setlocal
cd /d "%~dp0"

echo ============================================================
echo   Epoch DOY Clock - Portable EXE Builder
echo ============================================================
echo.

where py.exe >nul 2>nul
if %errorlevel%==0 (
    set "PY=py -3"
) else (
    where python.exe >nul 2>nul
    if %errorlevel%==0 (
        set "PY=python"
    ) else (
        echo ERROR: Python 3 was not found.
        echo Install Python 3 for Windows from python.org and try again.
        echo.
        pause
        exit /b 1
    )
)

echo Using Python:
%PY% --version
echo.

echo Installing/updating PyInstaller for this user...
%PY% -m pip install --user --upgrade pyinstaller
if errorlevel 1 (
    echo.
    echo ERROR: PyInstaller installation failed.
    pause
    exit /b 1
)

echo.
echo Building portable EXE...
%PY% -m PyInstaller ^
    --noconfirm ^
    --clean ^
    --onefile ^
    --windowed ^
    --name "Epoch DOY Clock" ^
    epoch_doy_clock.py

if errorlevel 1 (
    echo.
    echo ERROR: Build failed.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo BUILD COMPLETE
echo.
echo Your portable executable is:
echo.
echo   %CD%\dist\Epoch DOY Clock.exe
echo.
echo You can copy that EXE anywhere and run it directly.
echo Its JSON settings files will be created beside the EXE.
echo ============================================================
echo.
explorer.exe "%CD%\dist"
pause
