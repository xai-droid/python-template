@echo off
REM --- Starte Python GUI für neue Python-Datei ohne Konsolenfenster ---

REM Prüfen, ob Python verfügbar ist
where python >nul 2>&1
if errorlevel 1 (
    echo Python nicht gefunden! Bitte sicherstellen, dass Python im PATH ist.
    pause
    exit /b
)

REM Python-Pfad dynamisch setzen
set PYTHON=python

REM Skript-Pfad relativ zum BAT
set SCRIPT="%~dp0create_python_new.py"

REM Zielverzeichnis übergeben, %V wird vom Kontextmenü übergeben
set TARGETDIR=%~1
if "%TARGETDIR%"=="" set TARGETDIR=%CD%

REM GUI starten ohne sichtbare CMD
start "" "%PYTHON%" "%SCRIPT%" "%TARGETDIR%"
