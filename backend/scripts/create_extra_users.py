import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

def create_user_if_missing(username, password, role):
    if not User.objects.filter(username=username).exists():
        u = User.objects.create_user(username, f'{username}@tailleurs.com', password)
        u.role = role
        u.is_active = True
        u.save()
        print(f"✅ Created {role}: {username}")
    else:
        print(f"ℹ️ User already exists: {username}")

print("--- ADJUSTING USERS TO TARGET: 5 TOTAL (1 Admin, 1 Analista, 3 Empleados) ---")

# 1 Admin (Existing: admin)
create_user_if_missing('admin', 'admin123', 'admin')

# 1 Analista (Existing: analista)
create_user_if_missing('analista', 'analista123', 'analyst')

# 3 Empleados (Existing: empleado) -> Need 2 more
create_user_if_missing('empleado', 'empleado123', 'employee')
create_user_if_missing('empleado2', 'empleado123', 'employee')
create_user_if_missing('empleado3', 'empleado123', 'employee')

print(f"Total Users: {User.objects.count()}")
print("--- COMPLETE ---")
