@echo off
setlocal EnableExtensions EnableDelayedExpansion

echo === Installation: Neue Python-Datei erstellen ===
echo.

REM --------------------------------------------------
REM Zielverzeichnis (benutzerbezogen, stabil)
REM --------------------------------------------------
set "INSTALL_DIR=%LOCALAPPDATA%\PythonNew"

echo Installationsverzeichnis:
echo %INSTALL_DIR%
echo.

REM --------------------------------------------------
REM Ordner anlegen
REM --------------------------------------------------
mkdir "%INSTALL_DIR%" >nul 2>&1
mkdir "%INSTALL_DIR%\templates" >nul 2>&1

REM --------------------------------------------------
REM Dateien kopieren
REM --------------------------------------------------
copy "%~dp0create_python_new.bat" "%INSTALL_DIR%" /Y >nul
copy "%~dp0create_python_new.py"  "%INSTALL_DIR%" /Y >nul

if exist "%~dp0templates\" (
    xcopy "%~dp0templates\*" "%INSTALL_DIR%\templates\" /E /I /Y >nul
)

REM --------------------------------------------------
REM App Paths registrieren (wichtig!)
REM --------------------------------------------------
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\App Paths\create_python_new.bat" ^
 /ve /d "%INSTALL_DIR%\create_python_new.bat" /f >nul

reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\App Paths\create_python_new.bat" ^
 /v Path /d "%INSTALL_DIR%" /f >nul

REM --------------------------------------------------
REM Hintergrund-Kontextmenü (Explorer-Hintergrund)
REM --------------------------------------------------
reg add "HKCU\Software\Classes\Directory\Background\shell\PythonNewFile" ^
 /ve /d "Neue Python-Datei erstellen…" /f >nul

reg add "HKCU\Software\Classes\Directory\Background\shell\PythonNewFile" ^
 /v Icon /d "%SystemRoot%\System32\shell32.dll,70" /f >nul

reg add "HKCU\Software\Classes\Directory\Background\shell\PythonNewFile\command" ^
 /ve /d "create_python_new.bat \"%%V\"" /f >nul

REM --------------------------------------------------
REM Explorer aktualisieren (sanft)
REM --------------------------------------------------
ie4uinit.exe -show >nul 2>&1

echo.
echo Installation abgeschlossen.
echo Der Eintrag ist jetzt verfügbar unter:
echo Rechtsklick → Weitere Optionen anzeigen → Neue Python-Datei erstellen…
echo.

pause
endlocal
