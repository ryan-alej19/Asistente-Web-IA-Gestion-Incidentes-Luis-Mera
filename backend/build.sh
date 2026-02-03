#!/usr/bin/env bash 
set -o errexit 

echo "Instalando dependencias"
pip install -r requirements.txt

echo "Recopilando archivos estáticos"
python manage.py collectstatic --no-input --clear --verbosity 2

echo "Ejecutando migraciones"
python manage.py migrate --no-input

echo "Build completado"
