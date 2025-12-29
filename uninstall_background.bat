@echo off
setlocal EnableExtensions

echo Entferne Python-Neu-Hintergrundmenü...

REM --- Registry entfernen ---
reg delete "HKCU\Software\Classes\Directory\Background\shell\NeuePythonDatei" /f >nul 2>&1

REM --- Dateien entfernen ---
set INSTALL_DIR=%LOCALAPPDATA%\PythonNew
if exist "%INSTALL_DIR%" (
    rmdir /s /q "%INSTALL_DIR%"
)

echo.
echo Deinstallation abgeschlossen.
echo Explorer wird neu gestartet...

taskkill /f /im explorer.exe >nul
start explorer.exe

pause

