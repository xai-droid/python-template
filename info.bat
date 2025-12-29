@echo off
REM Ruft PowerShell auf und führt info.ps1 aus
powershell -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0\info.ps1"
pause


