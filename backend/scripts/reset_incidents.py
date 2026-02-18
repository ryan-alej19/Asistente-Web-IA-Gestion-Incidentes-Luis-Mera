
import os
import sys
import django

# Agregar directorio raíz al path para encontrar 'config'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from incidents.models import Incident, IncidentNote

def reset_db():
    print("--- BORRANDO TODOS LOS INCIDENTES ---")
    deleted_incidents = Incident.objects.all().delete()
    print(f"Eliminados: {deleted_incidents}")
    print("Base de datos limpia. Lista recibir nuevos casos.")

if __name__ == '__main__':
    reset_db()
