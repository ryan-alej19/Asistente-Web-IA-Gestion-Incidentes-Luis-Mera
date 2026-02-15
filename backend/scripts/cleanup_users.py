import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User

def cleanup_users():
    # Borrar usuario 'Analyst' si existe
    try:
        u = User.objects.get(username='Analyst')
        u.delete()
        print(" Usuario 'Analyst' eliminado.")
    except User.DoesNotExist:
        print("ℹ Usuario 'Analyst' no existe, no es necesario eliminar.")

    # Confirmar 'analista'
    if User.objects.filter(username='analista').exists():
        print(" Usuario 'analista' (analista123) está listo.")
    else:
        print(" Usuario 'analista' no encontrado. (Debería haber sido creado antes)")

if __name__ == '__main__':
    cleanup_users()
