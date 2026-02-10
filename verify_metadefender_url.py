import requests
import json

url = 'http://localhost:8000/api/incidents/analyze-url-preview/'
headers = {
    'Authorization': 'Token 66c551af5f94bf995e374fb8b9579a412908afc6',
    'Content-Type': 'application/json'
}
payload = {'url': 'https://google.com'}

print(f"Testing URL analysis for: {payload['url']}")
try:
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        # print("\n--- Analysis Result ---")
        # print(json.dumps(data, indent=2))
        
        engines = data.get('engines', [])
        md_found = any(e['name'] == 'MetaDefender' for e in engines)
        
        if md_found:
            print("\n[SUCCESS] MetaDefender found in engines list.")
            for e in engines:
                if e['name'] == 'MetaDefender':
                    print(f"MetaDefender details: {e}")
        else:
            print("\n[FAILURE] MetaDefender NOT found in engines list.")
            print("Engines found:", [e.get('name') for e in engines])
            
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

except Exception as e:
    print(f"Exception: {e}")
