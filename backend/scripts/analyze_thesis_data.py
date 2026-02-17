
import os
import django
import sys
from django.db.models import Count, Avg, Min, Max

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from incidents.models import Incident
from django.contrib.auth.models import User

def analyze_data():
    print("--- ANÁLISIS DE DATOS PARA TESIS ---")
    print("--- Fuente: Base de Datos Local (SQLite) ---")

    # 1. URLs Evaluadas
    total_urls = Incident.objects.filter(incident_type='url').count()
    unique_urls = Incident.objects.filter(incident_type='url').values('url').distinct().count()
    print(f"\n[2. URLS EVALUADAS]")
    print(f"Total de análisis de URLs: {total_urls}")
    print(f"URLs únicas investigadas: {unique_urls}")

    # 4. Número de Incidentes
    total_incidents = Incident.objects.count()
    total_files = Incident.objects.filter(incident_type='file').count()
    unique_incidents = unique_urls + total_files # Aproximación, asumiendo archivos distintos
    
    print(f"\n[4. NÚMERO DE INCIDENTES]")
    print(f"Interacciones totales (Incidentes registrados): {total_incidents}")
    print(f"Incidentes únicos (URLs únicas + Archivos): {unique_incidents}")
    print(f"  - URLs: {total_urls} (Únicas: {unique_urls})")
    print(f"  - Archivos: {total_files}")

    # 5. Usuarios
    total_users = User.objects.count()
    # Usuarios con incidentes creados
    active_users_count = Incident.objects.values('reported_by').distinct().count()
    
    print(f"\n[5. USUARIOS QUE VALIDARON]")
    print(f"Usuarios registrados en sistema: {total_users}")
    print(f"Usuarios activos (que generaron reportes): {active_users_count}")
    
    # Detalle de usuarios activos
    print("Detalle de actividad por usuario:")
    active_users = User.objects.filter(incidents__isnull=False).distinct()
    for u in active_users:
        count = Incident.objects.filter(reported_by=u).count()
        print(f"  - {u.username}: {count} reportes")

if __name__ == '__main__':
    analyze_data()
