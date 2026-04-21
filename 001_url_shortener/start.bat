@echo off
cd /d "%~dp0"

:: Browser nach 2 Sekunden öffnen (läuft parallel im Hintergrund)
start "" cmd /c "timeout /t 2 /nobreak >nul && start http://localhost:5000"

:: Flask starten
python -m src.main serve
pause
