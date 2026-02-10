import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

User = get_user_model()

try:
    user = User.objects.get(username='verification_user')
except User.DoesNotExist:
    try:
        user = User.objects.get(username='admin')
    except User.DoesNotExist:
        user = User.objects.create_superuser('admin', 'admin@example.com', 'admin')

token, created = Token.objects.get_or_create(user=user)
print(f"Token: {token.key}")
