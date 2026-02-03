@echo off
cd /d "%~dp0backend"
call venv\Scripts\activate
echo Iniciando Servidor Django...
python manage.py runserver
pause
