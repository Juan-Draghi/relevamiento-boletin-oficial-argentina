@echo off
setlocal
cd /d "%~dp0"

echo Instalando herramientas de build...
python -m pip install -r desktop_app\build_requirements.txt
if errorlevel 1 (
  echo.
  echo No se pudieron instalar las herramientas de build.
  pause
  exit /b 1
)

echo.
echo Generando ejecutable...
python -m PyInstaller ^
  --noconfirm ^
  --clean ^
  --onefile ^
  --name RelevamientoBORA ^
  --icon "desktop_app\static\app-icon.ico" ^
  --add-data "desktop_app\templates;templates" ^
  --add-data "desktop_app\static;static" ^
  --add-data "desktop_app\keywords.json;." ^
  --hidden-import desktop_app ^
  --hidden-import desktop_app.search_core ^
  desktop_app\app.py

if errorlevel 1 (
  echo.
  echo Fallo la generacion del ejecutable.
  pause
  exit /b 1
)

echo.
echo Ejecutable generado en dist\RelevamientoBORA.exe
pause
