@echo off
setlocal
cd /d "%~dp0"

rem Cierra cualquier copia previa de la app para no duplicarla en el puerto.
call "%~dp0stop_desktop.bat"

python desktop_app\app.py

if errorlevel 1 (
  echo.
  echo La aplicacion no pudo iniciarse. Si es la primera vez, ejecuta install_desktop.bat.
  pause
  exit /b 1
)
