@echo off
setlocal
cd /d "%~dp0"

python desktop_app\app.py

if errorlevel 1 (
  echo.
  echo La aplicacion no pudo iniciarse. Si es la primera vez, ejecuta install_desktop.bat.
  pause
  exit /b 1
)
