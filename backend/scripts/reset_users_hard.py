import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()


def reset_user(username, password, role, is_superuser=False):
    # Delete if exists
    if User.objects.filter(username=username).exists():
        User.objects.get(username=username).delete()
        print(f"Deleted existing user: {username}")
    
    # Create fresh
    if is_superuser:
        u = User.objects.create_superuser(username, f'{username}@test.com', password)
        u.role = role
        u.save()
        print(f"Created SUPERUSER: {username} / {password} (Role: {role})")
    else:
        u = User.objects.create_user(username, f'{username}@test.com', password)
        u.role = role
        u.is_active = True
        u.save()
        print(f"Created USER: {username} / {password} (Role: {role})")

# Execute resets
print("--- STARTING USER RESET ---")
reset_user('admin', 'admin123', 'admin', is_superuser=True)
reset_user('analista', 'analista123', 'analyst')
reset_user('empleado', 'empleado123', 'employee')
print("--- USER RESET COMPLETE ---")
