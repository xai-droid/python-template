@echo off
REM Wrapper für PythonNew
REM %~dp0 = Pfad des Batch-Skripts
set INSTALL_DIR=%~dp0
set TARGET_DIR=%1

if "%TARGET_DIR%"=="" (
    set TARGET_DIR=%CD%
)

REM Python-Skript ausführen
python "%INSTALL_DIR%create_python_new.py" "%TARGET_DIR%"


