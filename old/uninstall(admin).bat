@echo off
title Python Context Menu – Deinstallation
setlocal

:: Prüfen, ob Admin
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Starte Skript als Administrator...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

echo Entferne Python Context Menu...

REM --- Benutzer-Kontext (HKCU) ---
reg delete "HKCU\Software\Classes\.py\ShellNew" /f >nul 2>&1
reg delete "HKCU\Software\Classes\Python.File\shell\runwithpython" /f >nul 2>&1
reg delete "HKCU\Software\Classes\Python.File\shell\runwithpython\command" /f 2>nul
reg delete "HKCU\Software\Classes\Directory\Background\shell\NeuePythonDateiLeer" /f >nul 2>&1
reg delete "HKCU\Software\Classes\Directory\Background\shell\NeuePythonDateiLeer\command" /f 2>nul

REM --- System-Kontext (HKLM) ---
reg delete "HKLM\Software\Classes\.py\ShellNew" /f >nul 2>&1
reg delete "HKLM\Software\Classes\Python.File\shell\runwithpython" /f >nul 2>&1
reg delete "HKLM\Software\Classes\Python.File\shell\runwithpython\command" /f 2>nul
reg delete "HKLM\Software\Classes\Directory\Background\shell\NeuePythonDateiLeer" /f >nul 2>&1
reg delete "HKLM\Software\Classes\Directory\Background\shell\NeuePythonDateiLeer\command" /f 2>nul

echo Registry bereinigt.

REM --- Explorer neu starten ---
echo Starte Windows Explorer neu...
taskkill /f /im explorer.exe >nul 2>&1
start "" explorer.exe
ping 127.0.0.1 -n 2 >nul

REM --- Projektordner oeffnen ---
explorer.exe "%~dp0"

echo Fertig. Python Context Menu wurde entfernt.
echo Druecken Sie eine beliebige Taste zum Beenden...
pause >nul
exit
