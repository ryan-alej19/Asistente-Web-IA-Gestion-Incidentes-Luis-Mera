
import os
import django
import sys

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from users.models import UserProfile

def check_users():
    print("--- VERIFICANDO USUARIOS EN DB ---")
    users = User.objects.all()
    for u in users:
        print(f"Usuario: {u.username} (ID: {u.id})")
        if hasattr(u, 'profile'):
            print(f"  - Perfil encontrado. Listado Rol: '{u.profile.role}'")
        else:
            print("  - [ALERTA] NO TIENE PERFIL (UserProfile)")

if __name__ == '__main__':
    check_users()
