
import os
import django
import sys

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from incidents.models import Incident
from django.contrib.auth.models import User

def populate():
    print("--- PREPARANDO SISTEMA PARA USO MANUAL (LIMPIEZA) ---")
    
    # 1. Limpiar todos los incidentes (Solicitud de Usuario)
    count = Incident.objects.count()
    print(f"Eliminando {count} incidentes existentes para dejar la DB vacía...")
    Incident.objects.all().delete()
    
    # 2. Asegurar que existan los usuarios base para poder loguearse
    print("Verificando usuarios del sistema...")
    users_to_check = [
        {'username': 'empleado', 'email': 'empleado@tecnicontrol.com', 'role': 'employee'},
        {'username': 'analista', 'email': 'analista@tecnicontrol.com', 'role': 'analyst'},
        {'username': 'admin', 'email': 'admin@tecnicontrol.com', 'role': 'admin'}
    ]

    for u_data in users_to_check:
        try:
            user = User.objects.get(username=u_data['username'])
            print(f"Usuario '{u_data['username']}' verificado: OK")
        except User.DoesNotExist:
            print(f"Creando usuario '{u_data['username']}'...")
            user = User.objects.create_user(u_data['username'], u_data['email'], f"{u_data['username']}123")
            # Asegurar perfil si es necesario (el signal post_save debería manejarlo, pero por si acaso)
            if not hasattr(user, 'profile'):
                from users.models import UserProfile
                UserProfile.objects.create(user=user, role=u_data['role'])
            else:
                user.profile.role = u_data['role']
                user.profile.save()

    print("\n--- SISTEMA LIMPIO Y LISTO ---")
    print("Base de datos de incidentes vaciada. Usuarios listos para ingreso manual.")

if __name__ == '__main__':
    populate()
