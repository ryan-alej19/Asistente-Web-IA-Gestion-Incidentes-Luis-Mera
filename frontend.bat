@echo off
REM Ir al directorio del script
cd /d "%~dp0frontend"

REM Verificar existencia de node_modules
if not exist "node_modules" (
    echo [ERROR] No se encontraron dependencias.
    echo Ejecutando 'npm install'...
    call npm install
)

echo Iniciando Frontend React...
"C:\Program Files\nodejs\npm.cmd" start
pause
