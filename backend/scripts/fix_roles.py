
import os
import django
import sys

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from users.models import UserProfile

def fix():
    print("--- CORRIGIENDO ROLES (FIX) ---")
    
    try:
        u_admin = User.objects.get(username='admin')
        p_admin, _ = UserProfile.objects.get_or_create(user=u_admin)
        p_admin.role = 'admin'
        p_admin.save()
        print("Admin corregido.")
    except Exception as e:
        print(f"Error admin: {e}")

    try:
        u_analyst = User.objects.get(username='analista')
        p_analyst, _ = UserProfile.objects.get_or_create(user=u_analyst)
        p_analyst.role = 'analyst'
        p_analyst.save()
        print("Analista corregido.")
    except Exception as e:
        print(f"Error analista: {e}")

if __name__ == '__main__':
    fix()
