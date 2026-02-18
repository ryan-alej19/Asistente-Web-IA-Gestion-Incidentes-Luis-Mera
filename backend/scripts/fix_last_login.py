
import os
import sys
import django
from django.utils import timezone

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User

def fix_last_login():
    users_to_update = ['admin', 'analista', 'empleado', 'analyst']
    
    print("Corrigiendo last_login para usuarios principales...")
    
    for username in users_to_update:
        try:
            user = User.objects.get(username=username)
            # Solo actualizar si es None o si queremos forzar para la demo
            if not user.last_login:
                user.last_login = timezone.now()
                user.save()
                print(f"✅ [{username}] last_login actualizado a ahora.")
            else:
                # Opcional: Actualizar de todos modos para que se vea reciente en la demo
                user.last_login = timezone.now()
                user.save()
                print(f"🔄 [{username}] last_login refrescado a ahora.")
                
        except User.DoesNotExist:
            print(f"⚠️ Usuario {username} no encontrado.")

if __name__ == '__main__':
    fix_last_login()
