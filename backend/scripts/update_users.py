from django.contrib.auth import get_user_model
User = get_user_model()

# User: analista / analista123 (Role: analyst)
if not User.objects.filter(username='analista').exists():
    u = User.objects.create_user('analista', 'analista@test.com', 'analista123')
    u.role = 'analyst'
    u.save()
    print("User 'analista' created with role 'analyst'.")
else:
    u = User.objects.get(username='analista')
    u.set_password('analista123')
    u.role = 'analyst'
    u.save()
    print("User 'analista' updated.")

# User: empleado / empleado123 (Role: employee) - Already exists but updating to be sure
if User.objects.filter(username='empleado').exists():
    u = User.objects.get(username='empleado')
    u.set_password('empleado123')
    u.role = 'employee'
    u.save()
    print("User 'empleado' updated.")

# User: admin / admin123 (Role: admin)
if User.objects.filter(username='admin').exists():
    u = User.objects.get(username='admin')
    u.set_password('admin123')
    u.role = 'admin'
    u.save()
    print("User 'admin' updated.")
