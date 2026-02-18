
import requests
import json
import logging
import os
import sys
from decouple import config

# Setup paths
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

def test_gsb():
    print("--- TEST GOOGLE SAFE BROWSING ---")
    
    api_key = config('GOOGLE_SAFE_BROWSING_KEY', default=config('GEMINI_API_KEY'))
    print(f"API Key usada (parcial): {api_key[:10]}...")
    
    url_to_test = "http://malware.testing.google.test/testing/malware/"
    print(f"Probando URL: {url_to_test}")
    
    api_url = f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={api_key}"
    
    payload = {
        "client": {
            "clientId": "tesis-debug",
            "clientVersion": "1.0.0"
        },
        "threatInfo": {
            "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE"],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [
                {"url": url_to_test}
            ]
        }
    }
    
    try:
        response = requests.post(api_url, json=payload, timeout=15)
        print(f"Status Code: {response.status_code}")
        print("Respuesta Raw:")
        print(json.dumps(response.json(), indent=2))
        
        data = response.json()
        if 'matches' in data and len(data['matches']) > 0:
            print("\n✅ ÉXITO: Google detectó la amenaza.")
        else:
            print("\n❌ FALLO: Google devolvió seguro (o vacío).")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_gsb()
