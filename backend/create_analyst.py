import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from users.models import UserProfile

def create_analyst():
    username = 'analista'
    password = 'analista123'
    email = 'analista@tesis.com'
    
    # Check if exists
    if User.objects.filter(username=username).exists():
        print(f"El usuario '{username}' ya existe. Actualizando contraseña...")
        user = User.objects.get(username=username)
        user.set_password(password)
        user.save()
    else:
        print(f"Creando usuario '{username}'...")
        user = User.objects.create_user(username=username, email=email, password=password)
        
    # Ensure profile
    if not hasattr(user, 'profile'):
        UserProfile.objects.create(user=user, role='analyst')
    else:
        user.profile.role = 'analyst'
        user.profile.save()
        
    print(f"✅ Usuario '{username}' listo con rol de Analista.")

if __name__ == '__main__':
    create_analyst()
