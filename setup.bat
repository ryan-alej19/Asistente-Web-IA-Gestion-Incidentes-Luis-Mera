@echo off
echo Instalando dependencias del proyecto...

set "PROJECT_ROOT=%~dp0"
cd /d "%PROJECT_ROOT%"

echo.
echo [1/4] Creando entorno virtual...
python -m venv backend\venv

echo.
echo [2/4] Instalando dependencias backend...
call backend\venv\Scripts\activate
cd backend
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
cd ..

echo.
echo [3/4] Instalando dependencias frontend...
cd frontend
call npm install
cd ..

echo.
echo [4/4] Listo!
echo.
echo Ejecuta backend.bat para iniciar el servidor
echo Ejecuta frontend.bat para iniciar React
pause
