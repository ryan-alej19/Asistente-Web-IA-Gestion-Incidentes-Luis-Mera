import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from users.models import UserProfile

try:
    user = User.objects.get(username='analyst')
    print("User 'analyst' exists.")
    user.set_password('analyst123')
    user.save()
    print("Password set to 'analyst123'.")
    
    if not hasattr(user, 'profile'):
        UserProfile.objects.create(user=user, role='analyst')
        print("Profile created.")
    else:
        user.profile.role = 'analyst'
        user.profile.save()
        print("Profile role ensured as 'analyst'.")

except User.DoesNotExist:
    print("Creating user 'analyst'...")
    user = User.objects.create_user(username='analyst', email='analyst@example.com', password='analyst123')
    UserProfile.objects.create(user=user, role='analyst')
    print("User created.")
