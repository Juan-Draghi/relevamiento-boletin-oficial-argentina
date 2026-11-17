@echo off
setlocal
rem Detiene la aplicacion local (codigo fuente o RelevamientoBORA.exe):
rem cierra todo proceso que escuche en el puerto reservado de la app.
set "BORA_PORT=7861"

for /f "tokens=5" %%P in ('netstat -ano ^| findstr /R /C:":%BORA_PORT% .*LISTENING"') do (
  taskkill /PID %%P /F >nul 2>nul
)

exit /b
