:: Explorer beenden
taskkill /f /im explorer.exe

:: Cache löschen
del /f /q "%LOCALAPPDATA%\Microsoft\Windows\Explorer\*.db"

:: Explorer neu starten
start "" explorer.exe

explorer "%~dp0"

