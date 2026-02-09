@echo off
echo Iniciando Asistente de Ciberseguridad...
cd backend
:: Activar entorno virtual
call venv\Scripts\activate
:: Ejecutar servidor (Django leerá el .env automáticamente)
python manage.py runserver
pause
