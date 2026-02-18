
import requests
import json
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

def check_api():
    # Get token for analista
    user = User.objects.get(username='analista')
    token, _ = Token.objects.get_or_create(user=user)
    
    headers = {'Authorization': f'Token {token.key}'}
    
    # Check List
    url = 'http://127.0.0.1:8000/api/incidents/list/'
    print(f"GET {url}")
    
    try:
        res = requests.get(url, headers=headers)
        print(f"Status: {res.status_code}")
        
        data = res.json()
        if 'results' in data and len(data['results']) > 0:
            first = data['results'][0]
            print("\n--- FIRST INCIDENT STRUCTURE ---")
            print(json.dumps(first, indent=2))
            
            # Check unique types
            types = set(i.get('incident_type') for i in data['results'])
            print(f"\nUnique Types in Page 1: {types}")
            
        else:
            print("No results found or empty list.")
            print(data)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    check_api()
