import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from incidents.models import Incident

count = Incident.objects.count()
Incident.objects.all().delete()

print(f"✅ Cleared {count} incidents. Database is now empty of reports.")
