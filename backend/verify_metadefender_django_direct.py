import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
try:
    django.setup()
except Exception as e:
    print(f"Django setup error: {e}")
    # Might fail if settings are already configured or something, but usually fine in script.

from services.metadefender_service import MetaDefenderService

def test():
    md = MetaDefenderService()
    url = "https://google.com"
    print(f"Testing URL (Direct): {url}")
    
    # Analyze
    result = md.analyze_url(url)
    print("Result:", result)
    
    if result.get('source') == 'MetaDefender':
        print("[SUCCESS] MetaDefender Analysis Successful via Direct Call")
    else:
        print("[FAILURE] MetaDefender Analysis Failed via Direct Call")

if __name__ == "__main__":
    test()
