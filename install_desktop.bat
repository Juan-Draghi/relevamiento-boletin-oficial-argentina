@echo off
setlocal
cd /d "%~dp0"

python -m pip install -r desktop_app\requirements.txt

if errorlevel 1 (
  echo.
  echo No se pudieron instalar las dependencias.
  pause
  exit /b 1
)

echo.
echo Dependencias instaladas correctamente.
pause
