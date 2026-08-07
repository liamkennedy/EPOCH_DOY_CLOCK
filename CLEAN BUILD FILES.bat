@echo off
cd /d "%~dp0"
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist "Epoch DOY Clock.spec" del /q "Epoch DOY Clock.spec"
echo PyInstaller build files removed.
pause
