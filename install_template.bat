@echo off
SETLOCAL

:: --- 1. Template-Ordner erstellen ---
SET "SCRIPT_DIR=%~dp0"
SET "TEMPLATES_DIR=%SCRIPT_DIR%templates"
IF NOT EXIST "%TEMPLATES_DIR%" mkdir "%TEMPLATES_DIR%"

:: --- 2. Registry-Datei für Hintergrund-Menü erstellen ---
SET "REG_FILE=%SCRIPT_DIR%python_background_context.reg"

(
echo Windows Registry Editor Version 5.00
echo.
echo [HKEY_CURRENT_USER\Software\Classes\Directory\Background\shell\NeuePythonDatei_Hintergrund]
echo @="Neue Python-Datei (Hintergrund)"
echo "Icon"="python.exe"
echo "Position"="Top"
echo.
echo [HKEY_CURRENT_USER\Software\Classes\Directory\Background\shell\NeuePythonDatei_Hintergrund\command]
echo @="\"%SCRIPT_DIR%create_python_new.py\" \"%%V\""
) > "%REG_FILE%"

:: --- 3. Registry importieren ---
reg import "%REG_FILE%"

:: --- 4. Explorer neu starten ---
taskkill /f /im explorer.exe
start explorer.exe

echo Fertig! Rechtsklick -> Hintergrund -> "Neue Python-Datei (Hintergrund)" sollte jetzt funktionieren.
pause
ENDLOCAL
