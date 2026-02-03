import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model

def create_users():
    User = get_user_model()
    
    # Admin
    if not User.objects.filter(username='admin').exists():
        admin = User.objects.create_superuser('admin', 'admin@test.com', 'admin123')
        # Admin gets admin profile by default or we set it?
        # Let's clean it.
        if hasattr(admin, 'profile'):
            admin.profile.role = 'admin'
            admin.profile.save()
        print("Superuser 'admin' created.")
    else:
        print("Superuser 'admin' already exists.")

    # Analyst
    if not User.objects.filter(username='analyst').exists():
        u = User.objects.create_user('analyst', 'analyst@test.com', 'analyst123')
        if hasattr(u, 'profile'):
            u.profile.role = 'analyst'
            u.profile.save()
        print("User 'analyst' created.")
    else:
        print("User 'analyst' already exists.")

    # Employee
    if not User.objects.filter(username='empleado').exists():
        u = User.objects.create_user('empleado', 'employee@test.com', 'empleado123')
        if hasattr(u, 'profile'):
            u.profile.role = 'employee' # Enum values in model: 'employee', 'analyst', 'admin'
            u.profile.save()
        print("User 'empleado' created.")
    else:
        print("User 'empleado' already exists.")

if __name__ == '__main__':
    create_users()
