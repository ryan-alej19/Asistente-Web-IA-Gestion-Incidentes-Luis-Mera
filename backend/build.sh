#!/usr/bin/env bash 
set -o errexit 
# Instalar dependencias
pip install -r requirements.txt

# Recopilar archivos estáticos
python manage.py collectstatic --no-input

# Ejecutar migraciones de base de datos
python manage.py migrate 
