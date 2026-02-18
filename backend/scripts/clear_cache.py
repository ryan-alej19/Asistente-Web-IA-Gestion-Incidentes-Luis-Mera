
import os
import sys
import django

# Agregar directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from incidents.models import AnalysisCache

def clear_cache():
    count = AnalysisCache.objects.count()
    print(f"--- LIMPIANDO CASHÉ DE ANÁLISIS ---")
    print(f"Entradas encontradas: {count}")
    AnalysisCache.objects.all().delete()
    print("✅ Caché eliminado. Todas las nuevas consultas irán directo a las APIs (o overrides).")

if __name__ == '__main__':
    clear_cache()
