@echo off
setlocal EnableExtensions

echo Installiere Python-Neu-Hintergrundmenü...

REM --- Zielverzeichnis ---
set INSTALL_DIR=%LOCALAPPDATA%\PythonNew

mkdir "%INSTALL_DIR%" >nul 2>&1
mkdir "%INSTALL_DIR%\templates" >nul 2>&1

REM --- Dateien kopieren ---
copy "%~dp0create_python_new.bat" "%INSTALL_DIR%" /Y >nul
copy "%~dp0create_python_new.py"  "%INSTALL_DIR%" /Y >nul
xcopy "%~dp0templates\*" "%INSTALL_DIR%\templates\" /E /I /Y >nul

REM --- Registry setzen ---
reg add "HKCU\Software\Classes\Directory\Background\shell\NeuePythonDatei" ^
 /ve /d "Neue Python-Datei erstellen…" /f

reg add "HKCU\Software\Classes\Directory\Background\shell\NeuePythonDatei" ^
 /v Icon /d "python.exe" /f

reg add "HKCU\Software\Classes\Directory\Background\shell\NeuePythonDatei\command" ^
 /ve /d "\"%LOCALAPPDATA%\PythonNew\create_python_new.bat\" \"%%V\"" /f

echo.
echo Installation abgeschlossen.
echo Explorer wird neu gestartet...

taskkill /f /im explorer.exe >nul
start explorer.exe

pause
